from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
import re

import typer
import yaml
from rich.console import Console
from rich.table import Table

from ..engine import nodes, registry
from ..engine.workspace import require_workspace

console = Console()
_STALE_DAYS = 180


def run() -> None:
    """High-level health and coverage snapshot of the graph."""
    workspace = require_workspace()
    reg = registry.read(workspace)

    if not reg:
        console.print("[dim]Graph is empty. Run `kg init` then tell your agent: Process new data.[/dim]")
        return

    # --- counts ---
    type_counts: Counter = Counter(e.type for e in reg.values())
    clearance_counts: Counter = Counter(e.clearance for e in reg.values())
    discipline_counts: Counter = Counter(e.discipline or "Uncategorised" for e in reg.values())

    # --- stale check (read YAML blocks) ---
    today = date.today()
    stale_cutoff = today - timedelta(days=_STALE_DAYS)
    stale_nodes = []
    for node_path in nodes.all_nodes(workspace):
        raw = nodes.read_frontmatter_raw(node_path, max_lines=30)
        fm: dict = {}
        if raw.startswith("---"):
            try:
                end = raw.index("\n---", 3)
                fm = yaml.safe_load(raw[4:end]) or {}
            except (ValueError, yaml.YAMLError):
                pass
        lv = fm.get("last_verified")
        if lv:
            try:
                if date.fromisoformat(str(lv).strip()) < stale_cutoff:
                    stale_nodes.append(node_path.name)
            except ValueError:
                pass

    # --- query log stats ---
    query_log = workspace / "03_indexes/query_log.md"
    total_queries = 0
    gaps_found = 0
    keyword_freq: Counter = Counter()
    if query_log.exists():
        for line in query_log.read_text(encoding="utf-8").splitlines():
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 7 and cols[1] and cols[1] not in ("Date", "---"):
                total_queries += 1
                if cols[6] and cols[6].lower() not in ("none", "—", ""):
                    gaps_found += 1
                for word in re.findall(r"\b\w{4,}\b", cols[2].lower()):
                    keyword_freq[word] += 1

    # --- render ---
    console.print()
    console.print(f"[bold]Graph Summary[/bold]  —  {len(reg)} total nodes\n")

    # by type
    t1 = Table(show_header=True, header_style="bold dim", box=None, pad_edge=False)
    t1.add_column("Type", min_width=20)
    t1.add_column("Count", justify="right")
    for typ, cnt in type_counts.most_common():
        t1.add_row(typ, str(cnt))
    console.print("[bold]By type[/bold]")
    console.print(t1)
    console.print()

    # by discipline
    t2 = Table(show_header=True, header_style="bold dim", box=None, pad_edge=False)
    t2.add_column("Discipline", min_width=24)
    t2.add_column("Nodes", justify="right")
    t2.add_column("Note", style="dim")
    for disc, cnt in discipline_counts.most_common():
        note = "[yellow]isolated — no cross-links possible[/yellow]" if cnt == 1 else ""
        t2.add_row(disc, str(cnt), note)
    console.print("[bold]By discipline[/bold]")
    console.print(t2)
    console.print()

    # by clearance
    _color = {"public": "green", "internal": "yellow", "confidential": "red", "external": "blue"}
    t3 = Table(show_header=True, header_style="bold dim", box=None, pad_edge=False)
    t3.add_column("Clearance", min_width=14)
    t3.add_column("Count", justify="right")
    for cl, cnt in clearance_counts.most_common():
        c = _color.get(cl, "white")
        t3.add_row(f"[{c}]{cl}[/{c}]", str(cnt))
    console.print("[bold]By clearance[/bold]")
    console.print(t3)
    console.print()

    # staleness
    if stale_nodes:
        console.print(f"[yellow]⚠ {len(stale_nodes)} stale node(s)[/yellow] (not verified in 6+ months) — run [cyan]`kg flag-stale`[/cyan]")
    else:
        console.print("[green]✓ No stale nodes[/green]")
    console.print()

    # query stats
    console.print(f"[bold]Query log[/bold]  —  {total_queries} total  |  {gaps_found} with gaps")
    if keyword_freq:
        top = ", ".join(w for w, _ in keyword_freq.most_common(5))
        console.print(f"  Top keywords: [dim]{top}[/dim]")
    console.print()

    # one-paragraph plain summary
    thin = [d for d, c in discipline_counts.items() if c == 1]
    strong = [d for d, c in discipline_counts.most_common(3)]
    summary_parts = [f"The graph contains {len(reg)} nodes across {len(discipline_counts)} discipline(s)."]
    if strong:
        summary_parts.append(f"Best-covered areas: {', '.join(strong)}.")
    if thin:
        summary_parts.append(f"Thin areas (single node): {', '.join(thin)} — consider adding more sources.")
    if gaps_found:
        summary_parts.append(f"{gaps_found} past queries hit gaps — these are good candidates for new ingestion.")
    console.print("[bold]Coverage assessment[/bold]")
    console.print("  " + " ".join(summary_parts))
    console.print()
