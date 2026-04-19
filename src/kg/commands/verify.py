from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from ..engine.nodes import update_field
from ..engine.workspace import require_workspace

console = Console()


def _resolve_node(workspace: Path, name: str) -> Path | None:
    """Find a node file by stem or full filename."""
    nodes_dir = workspace / "02_nodes"
    stem = Path(name).stem  # handles both "my_node" and "my_node.md"
    exact = nodes_dir / f"{stem}.md"
    if exact.exists():
        return exact

    # fuzzy: match stem case-insensitively
    for path in nodes_dir.glob("*.md"):
        if path.stem.lower() == stem.lower():
            return path
    return None


def run(
    node: str = typer.Argument(..., help="Node filename or stem (e.g. my_node or my_node.md)"),
) -> None:
    """Stamp last_verified to today without changing node content."""
    workspace = require_workspace()
    node_path = _resolve_node(workspace, node)

    if node_path is None:
        console.print(f"[red]Error:[/red] node '{node}' not found in 02_nodes/", highlight=False)
        # suggest closest matches
        candidates = [p.stem for p in (workspace / "02_nodes").glob("*.md")]
        close = [c for c in candidates if node.lower() in c.lower()]
        if close:
            console.print("  Did you mean one of: " + ", ".join(close[:5]))
        raise typer.Exit(1)

    today = str(date.today())
    update_field(node_path, "last_verified", today)
    console.print(f"[green]✓[/green] [[{node_path.stem}]] verified on {today}")
