from pathlib import Path

import typer
from rich.console import Console

from ..engine import manifest, registry
from ..engine.atomic import atomic_write
from ..engine.nodes import replace_wikilink, all_nodes
from ..engine.workspace import require_workspace

console = Console()


def run(
    old_name: str = typer.Argument(..., help="Current node filename stem (e.g. my_node)"),
    new_name: str = typer.Argument(..., help="New node filename stem (e.g. better_name)"),
) -> None:
    """Rename a node and cascade the change to all indexes and WikiLinks."""
    workspace = require_workspace()
    nodes_dir = workspace / "02_nodes"

    old_stem = Path(old_name).stem
    new_stem = Path(new_name).stem
    old_path = nodes_dir / f"{old_stem}.md"
    new_path = nodes_dir / f"{new_stem}.md"

    if not old_path.exists():
        console.print(f"[red]Error:[/red] '{old_stem}.md' not found in 02_nodes/", highlight=False)
        raise typer.Exit(1)

    if new_path.exists():
        console.print(
            f"[red]Error:[/red] '{new_stem}.md' already exists. "
            "Use `Merge nodes` if you want to consolidate them.",
            highlight=False,
        )
        raise typer.Exit(1)

    # --- 1. update title field in YAML and write as new filename ---
    text = old_path.read_text(encoding="utf-8")
    import re
    text = re.sub(
        r'^(title:\s*)(.*)$',
        lambda m: m.group(1) + new_stem.replace("_", " ").title(),
        text, count=1, flags=re.MULTILINE,
    )
    new_path.write_text(text, encoding="utf-8")

    # --- 2. cascade WikiLink replacements in all other nodes ---
    updated_nodes = 0
    for node_path in all_nodes(workspace):
        if node_path.name in (old_path.name, new_path.name):
            continue
        node_text = node_path.read_text(encoding="utf-8")
        if f"[[{old_stem}]]" in node_text:
            new_text = replace_wikilink(node_text, old_stem, new_stem)
            node_path.write_text(new_text, encoding="utf-8")
            updated_nodes += 1

    # --- 3. update node_registry.md ---
    reg = registry.read(workspace)
    old_file = f"{old_stem}.md"
    new_file = f"{new_stem}.md"
    if old_file in reg:
        entry = reg.pop(old_file)
        entry.file = new_file
        entry.title = new_stem.replace("_", " ").title()
        reg[new_file] = entry
        registry.write(workspace, reg)

    # --- 4. update input_manifest.md ---
    mf = manifest.read(workspace)
    for source_file, entry in mf.items():
        if entry.node_file == old_file:
            entry.node_file = new_file
    manifest.write(workspace, mf)

    # --- 5. update master_index.md ---
    mi_path = workspace / "03_indexes/master_index.md"
    if mi_path.exists():
        mi_text = mi_path.read_text(encoding="utf-8")
        mi_text = replace_wikilink(mi_text, old_stem, new_stem)
        mi_path.write_text(mi_text, encoding="utf-8")

    # --- 6. delete old file ---
    old_path.unlink()

    console.print(
        f"[green]✓[/green] Renamed [[{old_stem}]] → [[{new_stem}]]  "
        f"({updated_nodes} cross-reference(s) updated)"
    )
