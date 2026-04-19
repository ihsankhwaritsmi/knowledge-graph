from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from ..engine import nodes
from ..engine.workspace import require_workspace

console = Console()

_STALE_DAYS = 180
_AGING_DAYS = 90


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def run(
    stale_only: bool = typer.Option(False, "--stale-only", "-s", help="Show only STALE nodes (>6 months)"),
) -> None:
    """Audit the graph for nodes that haven't been verified recently."""
    workspace = require_workspace()
    today = date.today()
    stale_cutoff = today - timedelta(days=_STALE_DAYS)
    aging_cutoff = today - timedelta(days=_AGING_DAYS)

    buckets: defaultdict[str, list[dict]] = defaultdict(list)

    for node_path in nodes.all_nodes(workspace):
        raw = nodes.read_frontmatter_raw(node_path, max_lines=30)
        # extract just the YAML block
        fm: dict = {}
        if raw.startswith("---"):
            try:
                end = raw.index("\n---", 3)
                fm = yaml.safe_load(raw[4:end]) or {}
            except (ValueError, yaml.YAMLError):
                pass

        last_verified = _parse_date(fm.get("last_verified"))
        title = fm.get("title") or node_path.stem
        discipline = fm.get("discipline") or "—"

        entry = {"file": node_path.name, "title": title, "discipline": discipline, "last_verified": last_verified}

        if last_verified is None:
            buckets["UNKNOWN"].append(entry)
        elif last_verified < stale_cutoff:
            buckets["STALE"].append(entry)
        elif last_verified < aging_cutoff:
            if not stale_only:
                buckets["AGING"].append(entry)
        else:
            if not stale_only:
                buckets["CURRENT"].append(entry)

    def _make_table(title: str, color: str, rows: list[dict], show_date: bool = True) -> Table:
        t = Table(title=f"[bold {color}]{title}[/bold {color}] — {len(rows)} node(s)",
                  show_header=True, header_style="bold dim", box=None,
                  pad_edge=False, title_justify="left")
        t.add_column("File", style="dim", min_width=20)
        t.add_column("Title", min_width=20)
        t.add_column("Discipline", min_width=16)
        if show_date:
            t.add_column("Last Verified")
        for r in rows:
            lv = str(r["last_verified"]) if r["last_verified"] else "—"
            row_data = [r["file"], r["title"], r["discipline"]]
            if show_date:
                row_data.append(lv)
            t.add_row(*row_data)
        return t

    console.print()

    if buckets["STALE"]:
        console.print(_make_table("Stale  (> 6 months)", "red", buckets["STALE"]))
        console.print()
    if buckets["AGING"] and not stale_only:
        console.print(_make_table("Aging  (3 – 6 months)", "yellow", buckets["AGING"]))
        console.print()
    if buckets["UNKNOWN"]:
        console.print(_make_table("Unknown  (no date)", "dim", buckets["UNKNOWN"], show_date=False))
        console.print()
    if buckets["CURRENT"] and not stale_only:
        console.print(f"[green]Current (< 3 months):[/green] {len(buckets['CURRENT'])} node(s) — all good")
        console.print()

    stale_n = len(buckets["STALE"])
    unknown_n = len(buckets["UNKNOWN"])
    if stale_n or unknown_n:
        console.print(
            f"[bold]Recommendation:[/bold] run [cyan]`kg verify <node>`[/cyan] after confirming "
            f"each stale node is still accurate."
        )
    else:
        console.print("[green]✓ All nodes are current.[/green]")
    console.print()
