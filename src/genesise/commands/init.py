from pathlib import Path

import typer
from ..console import console

from ..engine.workspace import DIRS

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


_INDEX_TEMPLATES: dict[str, str] = {
    "03_indexes/master_index.md": (
        "# Master Index\n"
        "Root Map of Content (MOC) for the Universal Knowledge Graph.\n"
    ),
    "03_indexes/node_registry.md": (
        "# Node Registry\n"
        "One row per node. Primary retrieval index — read this on every query.\n\n"
        "| File | Title | Type | Discipline | Clearance | Tags | Summary |\n"
        "|---|---|---|---|---|---|---|\n"
    ),
    "03_indexes/cluster_index.md": (
        "# Discipline Cluster Index\n"
        "Pre-filter for large graphs (50+ nodes). One row per discipline.\n"
        "Read this BEFORE node_registry.md to narrow candidates by discipline.\n\n"
        "| Discipline | Node Count | Coverage Summary |\n"
        "|---|---|---|\n"
    ),
    "03_indexes/input_manifest.md": (
        "# Input Manifest\n"
        "Tracks every source file ever seen in 01_raw_inputs/ and the node it produced.\n"
        'Used by "Sync graph" to detect changes between sessions.\n\n'
        "| Source File | Node File | Date Added | SHA-256 |\n"
        "|---|---|---|---|\n"
    ),
    "03_indexes/query_log.md": (
        "# Query Log\n"
        "Append-only log of every query run against the graph.\n"
        "Use this to spot frequently accessed nodes and recurring gaps.\n\n"
        "| Date | Query | Mode | Nodes Hit | Confidence | Gaps |\n"
        "|---|---|---|---|---|---|\n"
    ),
    "03_indexes/source_config.md": (
        "# Source & Gap-Fill Configuration\n\n"
        "## Gap-Fill Mode\n"
        "# Options: parametric (default) | external | none\n"
        "gap_fill_mode: parametric\n\n"
        "## External Search (only applies when gap_fill_mode: external)\n"
        "auto_save_external: enabled\n\n"
        "## External Sources (priority order)\n"
        "# Open-access (always available):\n"
        "1. Wikipedia        — factual/encyclopedic\n"
        "2. ArXiv            — scientific/technical preprints\n"
        "3. DuckDuckGo       — general web\n"
        "4. PubMed           — biomedical and life sciences (free)\n"
        "5. Semantic Scholar — cross-discipline academic search (free)\n\n"
        "# Institutional (uncomment to enable — requires subscription or VPN):\n"
        "# 6. IEEE Xplore  — engineering, electronics, computer science\n"
        "# 7. Elsevier     — broad sciences (ScienceDirect)\n"
        "# 8. MDPI         — open-access multidisciplinary journals\n"
        "# 9. Springer     — broad sciences and engineering\n\n"
        "## API Keys (institutional sources only — leave blank if not available)\n"
        "ieee_api_key:\n"
        "elsevier_api_key:\n"
        "springer_api_key:\n\n"
        "## Custom Sources\n"
        "(none configured)\n"
    ),
}


def run(
    path: Path = typer.Argument(Path("."), help="Directory to initialize (default: current)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing index files"),
) -> None:
    """Initialize a kg workspace — creates folders and index files."""
    target = path.resolve()
    target.mkdir(parents=True, exist_ok=True)

    created_dirs, skipped_dirs = [], []
    created_files, skipped_files = [], []

    for d in DIRS:
        dp = target / d
        if dp.exists():
            skipped_dirs.append(d)
        else:
            dp.mkdir(parents=True, exist_ok=True)
            created_dirs.append(d)

    for fname, content in _INDEX_TEMPLATES.items():
        fp = target / fname
        if fp.exists() and not force:
            skipped_files.append(fname)
        else:
            fp.write_text(content, encoding="utf-8")
            created_files.append(fname)

    bootstrap_src = _TEMPLATES_DIR / "bootstrap.md"
    bootstrap_dst = target / "bootstrap.md"
    if bootstrap_src.exists():
        if bootstrap_dst.exists() and not force:
            skipped_files.append("bootstrap.md")
        else:
            bootstrap_dst.write_text(bootstrap_src.read_text(encoding="utf-8"), encoding="utf-8")
            created_files.append("bootstrap.md")

    console.print()
    console.print("[bold green]✓ Workspace ready[/bold green]", highlight=False)

    if created_dirs:
        console.print(f"  Created  [green]{len(created_dirs)}[/green] dir(s):  {', '.join(created_dirs)}")
    if skipped_dirs:
        console.print(f"  [dim]Skipped  {len(skipped_dirs)} dir(s) — already exist[/dim]")
    for f in created_files:
        console.print(f"  [green]+[/green] {f}")
    if skipped_files:
        console.print(
            f"  [dim]Skipped  {len(skipped_files)} index file(s) — already exist "
            f"(use --force to overwrite)[/dim]"
        )

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Open your agent and run:  [cyan]Read bootstrap.md and execute the instructions.[/cyan]")
    console.print("  2. Drop files into           [yellow]01_raw_inputs/[/yellow]")
    console.print("  3. Tell your agent:          [cyan]Process new data[/cyan]")
    console.print()
