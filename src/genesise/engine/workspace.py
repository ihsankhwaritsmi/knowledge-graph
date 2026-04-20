from pathlib import Path
import typer

WORKSPACE_MARKER = "03_indexes"
DIRS = ["01_raw_inputs", "02_nodes", "03_indexes", "04_synthesis"]


def find_workspace(start: Path | None = None) -> Path | None:
    """Walk up from start looking for a directory that contains 03_indexes/."""
    path = (start or Path.cwd()).resolve()
    while True:
        if (path / WORKSPACE_MARKER).is_dir():
            return path
        parent = path.parent
        if parent == path:
            return None
        path = parent


def require_workspace() -> Path:
    ws = find_workspace()
    if ws is None:
        typer.echo("Error: not inside a genesise workspace. Run `gns init` first.", err=True)
        raise typer.Exit(1)
    return ws
