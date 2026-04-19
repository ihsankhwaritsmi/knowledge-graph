from datetime import date
from pathlib import Path

import typer
from ..console import console
from rich.table import Table

from ..engine import manifest, registry, nodes
from ..engine.hashing import sha256
from ..engine.workspace import require_workspace



def _cascade_delete(workspace: Path, node_filename: str) -> int:
    """Remove all cross-references to node_filename from other nodes. Returns count updated."""
    stem = Path(node_filename).stem
    updated = 0
    for node_path in nodes.all_nodes(workspace):
        if node_path.name == node_filename:
            continue
        text = node_path.read_text(encoding="utf-8")
        if f"[[{stem}]]" in text:
            new_text = nodes.remove_wikilink(text, stem)
            # append deletion note to body
            note = f"\n> (source deleted: {node_filename})\n"
            new_text = new_text.rstrip() + note
            node_path.write_text(new_text, encoding="utf-8")
            updated += 1
    return updated


def _remove_from_master_index(workspace: Path, node_filename: str) -> None:
    stem = Path(node_filename).stem
    mi_path = workspace / "03_indexes/master_index.md"
    if not mi_path.exists():
        return
    text = mi_path.read_text(encoding="utf-8")
    new_text = nodes.remove_wikilink(text, stem)
    mi_path.write_text(new_text, encoding="utf-8")


def _decrement_cluster(workspace: Path, discipline: str) -> None:
    ci_path = workspace / "03_indexes/cluster_index.md"
    if not ci_path.exists() or not discipline:
        return
    lines = ci_path.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines = []
    for line in lines:
        cols = [c.strip() for c in line.split("|")]
        if len(cols) >= 3 and cols[1] == discipline and cols[2].isdigit():
            count = max(0, int(cols[2]) - 1)
            line = line.replace(f"| {cols[2]} |", f"| {count} |", 1)
        new_lines.append(line)
    ci_path.write_text("".join(new_lines), encoding="utf-8")


def run(
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
) -> None:
    """Detect changes in 01_raw_inputs/ and update the graph accordingly."""
    workspace = require_workspace()
    raw_dir = workspace / "01_raw_inputs"
    nodes_dir = workspace / "02_nodes"

    if not raw_dir.exists():
        console.print("[red]Error:[/red] 01_raw_inputs/ not found.", highlight=False)
        raise typer.Exit(1)

    manifest_entries = manifest.read(workspace)
    reg_entries = registry.read(workspace)

    # compute hashes for all files currently on disk
    disk: dict[str, str] = {}
    for f in raw_dir.iterdir():
        if f.is_file():
            disk[f.name] = sha256(f)

    new_files = [f for f in disk if f not in manifest_entries]
    updated_files = [f for f in disk if f in manifest_entries and disk[f] != manifest_entries[f].sha256]
    deleted_files = [f for f in manifest_entries if f not in disk]
    unchanged_files = [f for f in disk if f in manifest_entries and disk[f] == manifest_entries[f].sha256]

    # --- handle deletions (fully deterministic) ---
    cascaded_refs = 0
    for fname in deleted_files:
        entry = manifest_entries[fname]
        node_file = entry.node_file

        # cascade cross-references
        cascaded_refs += _cascade_delete(workspace, node_file)

        # remove from registry
        reg_entries.pop(node_file, None)

        # decrement cluster index
        node_path = nodes_dir / node_file
        if node_path.exists():
            fm, _ = nodes.read_frontmatter(node_path)
            _decrement_cluster(workspace, fm.get("discipline", ""))
            node_path.unlink()

        # remove from manifest
        del manifest_entries[fname]

        _remove_from_master_index(workspace, node_file)

    # --- update manifest hashes for updated files ---
    for fname in updated_files:
        manifest_entries[fname].sha256 = disk[fname]
        manifest_entries[fname].date_added = str(date.today())

    # persist changes
    if deleted_files or updated_files:
        manifest.write(workspace, manifest_entries)
        registry.write(workspace, reg_entries)

    # --- broken link scan ---
    broken: list[tuple[str, str]] = []
    for node_path in nodes.all_nodes(workspace):
        fm, _ = nodes.read_frontmatter(node_path)
        for field in ("connections", "contradicts"):
            for link in fm.get(field) or []:
                linked_stem = str(link).strip("[]")
                linked_file = f"{linked_stem}.md"
                if not (nodes_dir / linked_file).exists():
                    broken.append((node_path.name, link))

    # --- output ---
    if json_output:
        import json
        print(json.dumps({
            "new": new_files, "updated": updated_files,
            "deleted": deleted_files, "unchanged": unchanged_files,
            "broken_links": [{"node": n, "link": str(l)} for n, l in broken],
        }, indent=2))
        return

    console.print()
    console.print("[bold]Sync complete[/bold]")
    console.print(f"  [green]NEW      {len(new_files):>3}[/green]  → tell your agent: [cyan]Process new data[/cyan]")
    console.print(f"  [yellow]UPDATED  {len(updated_files):>3}[/yellow]  → tell your agent: [cyan]Process new data[/cyan]")
    console.print(f"  [red]DELETED  {len(deleted_files):>3}[/red]  → cascaded {cascaded_refs} cross-reference(s)")
    console.print(f"  [dim]UNCHANGED{len(unchanged_files):>3}[/dim]")

    if new_files or updated_files:
        console.print()
        console.print("  Files awaiting ingestion:")
        for f in new_files:
            console.print(f"    [green]+[/green] {f}")
        for f in updated_files:
            console.print(f"    [yellow]~[/yellow] {f}")

    if broken:
        console.print()
        console.print(f"  [red]⚠ {len(broken)} broken link(s) — run `kg lint` for details[/red]")

    console.print()
