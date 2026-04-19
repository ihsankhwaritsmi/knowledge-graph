from collections import defaultdict
from pathlib import Path

import typer
from ..console import console
from rich.table import Table

from ..engine import registry
from ..engine.workspace import require_workspace


_CLEARANCE_COLOR = {
    "public": "green",
    "internal": "yellow",
    "confidential": "red",
    "external": "blue",
}


def run(
    discipline: str = typer.Option("", "--discipline", "-d", help="Filter by discipline"),
    clearance: str = typer.Option("", "--clearance", "-c", help="Filter by clearance level"),
) -> None:
    """List all nodes grouped by discipline."""
    workspace = require_workspace()
    entries = registry.read(workspace)

    if not entries:
        console.print("[dim]No nodes in the graph yet. Run `Process new data` with your agent.[/dim]")
        return

    # apply filters
    if discipline:
        entries = {k: v for k, v in entries.items() if discipline.lower() in v.discipline.lower()}
    if clearance:
        entries = {k: v for k, v in entries.items() if clearance.lower() == v.clearance.lower()}

    grouped: defaultdict[str, list] = defaultdict(list)
    for e in entries.values():
        grouped[e.discipline or "Uncategorised"].append(e)

    console.print()
    total = 0
    for disc in sorted(grouped.keys()):
        group = grouped[disc]
        total += len(group)

        table = Table(
            title=f"[bold]{disc}[/bold]",
            show_header=True,
            header_style="bold dim",
            show_lines=False,
            box=None,
            pad_edge=False,
            title_justify="left",
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", min_width=20)
        table.add_column("Type", style="dim", min_width=14)
        table.add_column("Clearance", min_width=12)
        table.add_column("Summary")

        for i, e in enumerate(group, 1):
            color = _CLEARANCE_COLOR.get(e.clearance, "white")
            table.add_row(
                str(i),
                e.title or e.file,
                e.type,
                f"[{color}]{e.clearance}[/{color}]",
                e.summary[:80] + ("…" if len(e.summary) > 80 else ""),
            )

        console.print(table)
        console.print()

    filter_note = ""
    if discipline or clearance:
        filter_note = f" (filtered)"
    console.print(f"[dim]{total} node(s) across {len(grouped)} discipline(s){filter_note}[/dim]")
    console.print()
