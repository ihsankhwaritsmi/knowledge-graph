import re
from typing import Optional

import typer
from ..console import console
from ..engine.atomic import atomic_write
from ..engine.workspace import require_workspace

_VALID_MODES = ("parametric", "external", "none")

_DESCRIPTIONS = {
    "parametric": "model's trained knowledge — nothing leaves your machine (default)",
    "external":   "sanitized web search — data leaves machine only after clearance check",
    "none":       "report gaps only, do not attempt to fill them",
}

_COLORS = {
    "parametric": "green",
    "external":   "yellow",
    "none":       "dim",
}


def run(
    mode: Optional[str] = typer.Argument(
        None,
        help="New mode: parametric | external | none. Omit to view the current setting.",
    ),
) -> None:
    """View or set the gap-fill mode (parametric / external / none)."""
    workspace = require_workspace()
    config_path = workspace / "03_indexes/source_config.md"

    if not config_path.exists():
        console.print(
            "[red]Error:[/red] source_config.md not found. Run `gns init` first.",
            highlight=False,
        )
        raise typer.Exit(1)

    text = config_path.read_text(encoding="utf-8")
    match = re.search(r"^gap_fill_mode:\s*(\S+)", text, re.MULTILINE)
    current = match.group(1) if match else "unknown"

    if mode is None:
        c = _COLORS.get(current, "white")
        console.print(f"\nCurrent gap-fill mode: [{c}]{current}[/{c}]\n")
        for m, desc in _DESCRIPTIONS.items():
            marker = "→" if m == current else " "
            col = _COLORS[m]
            console.print(f"  {marker} [{col}]{m:<12}[/{col}]  {desc}")
        console.print(f"\nTo change: [cyan]gns gap-fill <mode>[/cyan]\n")
        return

    if mode not in _VALID_MODES:
        console.print(
            f"[red]Error:[/red] invalid mode '{mode}'. Choose: parametric | external | none",
            highlight=False,
        )
        raise typer.Exit(1)

    if not match:
        console.print(
            "[red]Error:[/red] gap_fill_mode line not found in source_config.md.",
            highlight=False,
        )
        raise typer.Exit(1)

    new_text = re.sub(
        r"^gap_fill_mode:\s*\S+",
        f"gap_fill_mode: {mode}",
        text,
        flags=re.MULTILINE,
    )
    atomic_write(config_path, new_text)

    c = _COLORS[mode]
    console.print(f"\n[green]✓[/green] Gap-fill mode → [{c}]{mode}[/{c}]")
    console.print(f"  [dim]{_DESCRIPTIONS[mode]}[/dim]")

    if mode == "external":
        console.print(
            "\n  [yellow]Note:[/yellow] queries are sanitized before leaving your machine.\n"
            "  Confidential nodes always block external search regardless of this setting.\n"
            "  Configure API keys and enabled sources in [cyan]03_indexes/source_config.md[/cyan]"
        )
    console.print()
