from dataclasses import dataclass
from pathlib import Path

from .atomic import atomic_write

_HEADER = (
    "# Node Registry\n"
    "One row per node. Primary retrieval index — read this on every query.\n\n"
    "| File | Title | Type | Discipline | Clearance | Tags | Summary |\n"
    "|---|---|---|---|---|---|---|\n"
)


@dataclass
class RegistryEntry:
    file: str
    title: str
    type: str
    discipline: str
    clearance: str
    tags: str
    summary: str


def path(workspace: Path) -> Path:
    return workspace / "03_indexes/node_registry.md"


def read(workspace: Path) -> dict[str, RegistryEntry]:
    entries: dict[str, RegistryEntry] = {}
    for line in path(workspace).read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in line.split("|")]
        # valid data row: 9 elements, not header, not separator
        if (
            len(cols) == 9
            and cols[1]
            and cols[1] != "File"
            and not cols[1].startswith("-")
        ):
            e = RegistryEntry(
                file=cols[1], title=cols[2], type=cols[3],
                discipline=cols[4], clearance=cols[5],
                tags=cols[6], summary=cols[7],
            )
            entries[e.file] = e
    return entries


def write(workspace: Path, entries: dict[str, RegistryEntry]) -> None:
    rows = "".join(
        f"| {e.file} | {e.title} | {e.type} | {e.discipline} "
        f"| {e.clearance} | {e.tags} | {e.summary} |\n"
        for e in entries.values()
    )
    atomic_write(path(workspace), _HEADER + rows)
