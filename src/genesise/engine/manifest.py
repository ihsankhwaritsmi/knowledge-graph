import re
from dataclasses import dataclass
from pathlib import Path

from .atomic import atomic_write

_HEADER = (
    "# Input Manifest\n"
    'Tracks every source file ever seen in 01_raw_inputs/ and the node it produced.\n'
    'Used by "Sync graph" to detect changes between sessions.\n\n'
    "| Source File | Node File | Date Added | SHA-256 |\n"
    "|---|---|---|---|\n"
)
_ROW_RE = re.compile(
    r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([a-fA-F0-9]{64})\s*\|"
)


@dataclass
class ManifestEntry:
    source_file: str
    node_file: str
    date_added: str
    sha256: str


def path(workspace: Path) -> Path:
    return workspace / "03_indexes/input_manifest.md"


def read(workspace: Path) -> dict[str, ManifestEntry]:
    entries: dict[str, ManifestEntry] = {}
    for line in path(workspace).read_text(encoding="utf-8").splitlines():
        m = _ROW_RE.match(line)
        if m:
            e = ManifestEntry(
                source_file=m.group(1).strip(),
                node_file=m.group(2).strip(),
                date_added=m.group(3).strip(),
                sha256=m.group(4).strip(),
            )
            entries[e.source_file] = e
    return entries


def write(workspace: Path, entries: dict[str, ManifestEntry]) -> None:
    rows = "".join(
        f"| {e.source_file} | {e.node_file} | {e.date_added} | {e.sha256} |\n"
        for e in entries.values()
    )
    atomic_write(path(workspace), _HEADER + rows)
