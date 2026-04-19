from pathlib import Path

import typer
from ..console import console
import yaml

from ..engine import nodes
from ..engine.workspace import require_workspace


_MANDATORY_FIELDS = ("summary", "date_added", "clearance")


def _check_yaml(node_path: Path) -> list[str]:
    errors = []
    text = node_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        errors.append("missing opening ---")
        return errors

    try:
        end = text.index("\n---", 3)
    except ValueError:
        errors.append("missing closing ---")
        return errors

    yaml_text = text[4:end]
    try:
        fm = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return errors

    for field in _MANDATORY_FIELDS:
        if not fm.get(field):
            errors.append(f"missing or empty field: {field}")

    return errors


def _check_table(index_path: Path) -> list[tuple[int, str]]:
    """Check that all data rows have the same column count as the header."""
    errors = []
    lines = index_path.read_text(encoding="utf-8").splitlines()
    header_cols = None
    for i, line in enumerate(lines, 1):
        if not line.startswith("|"):
            continue
        cols = line.split("|")
        if header_cols is None and "---" not in line:
            header_cols = len(cols)
            continue
        if "---" in line:
            continue
        if header_cols and len(cols) != header_cols:
            errors.append((i, f"expected {header_cols} columns, got {len(cols)}"))
    return errors


def _check_links(workspace: Path) -> list[tuple[str, str]]:
    broken = []
    nodes_dir = workspace / "02_nodes"
    for node_path in nodes.all_nodes(workspace):
        fm, _ = nodes.read_frontmatter(node_path)
        for field in ("connections", "contradicts"):
            for link in fm.get(field) or []:
                stem = str(link).strip("[]")
                if not (nodes_dir / f"{stem}.md").exists():
                    broken.append((node_path.name, str(link)))
    return broken


def run(
    fix: bool = typer.Option(False, "--fix", help="Auto-fix table rows (not implemented yet — report only)"),
) -> None:
    """Check all nodes for broken YAML, malformed index rows, and orphaned WikiLinks."""
    workspace = require_workspace()

    yaml_errors: dict[str, list[str]] = {}
    for node_path in nodes.all_nodes(workspace):
        errs = _check_yaml(node_path)
        if errs:
            yaml_errors[node_path.name] = errs

    table_errors: dict[str, list[tuple[int, str]]] = {}
    for idx_file in ("node_registry.md", "cluster_index.md"):
        idx_path = workspace / "03_indexes" / idx_file
        if idx_path.exists():
            errs = _check_table(idx_path)
            if errs:
                table_errors[idx_file] = errs

    broken_links = _check_links(workspace)

    total_nodes = len(list((workspace / "02_nodes").glob("*.md")))

    console.print()
    if yaml_errors:
        console.print("[bold red]YAML errors[/bold red]")
        for fname, errs in yaml_errors.items():
            for err in errs:
                console.print(f"  [red]✗[/red] {fname} — {err}")
        console.print()

    if table_errors:
        console.print("[bold red]Table errors[/bold red]")
        for fname, errs in table_errors.items():
            for row, err in errs:
                console.print(f"  [red]✗[/red] {fname} row {row} — {err}")
        console.print()

    if broken_links:
        console.print("[bold red]Broken WikiLinks[/bold red]")
        for node_file, link in broken_links:
            console.print(f"  [red]✗[/red] {node_file} → [[{link}]]")
        console.print()

    yaml_count = sum(len(v) for v in yaml_errors.values())
    table_count = sum(len(v) for v in table_errors.values())
    link_count = len(broken_links)
    total_errors = yaml_count + table_count + link_count

    status = "[green]✓ Clean[/green]" if total_errors == 0 else f"[red]✗ {total_errors} issue(s) found[/red]"
    console.print(
        f"{status}  —  {total_nodes} nodes checked  |  "
        f"{yaml_count} YAML  |  {table_count} table  |  {link_count} broken links"
    )
    console.print()

    if total_errors:
        raise typer.Exit(1)
