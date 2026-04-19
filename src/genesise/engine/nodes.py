import re
from pathlib import Path

import yaml

from .atomic import atomic_write


def read_frontmatter(path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text). Empty dict if no valid frontmatter."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}, text
    yaml_text = text[4:end]
    body = text[end + 4:].lstrip("\n")
    try:
        fm = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def read_frontmatter_raw(path: Path, max_lines: int = 30) -> str:
    """Return just the first max_lines of a file — cheap YAML block check."""
    lines = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_lines:
                break
            lines.append(line)
    return "".join(lines)


def update_field(path: Path, field: str, value: str) -> None:
    """Update a single YAML frontmatter field atomically."""
    text = path.read_text(encoding="utf-8")
    pattern = rf"^({re.escape(field)}:\s*)(.*)$"
    new_text = re.sub(pattern, rf"\g<1>{value}", text, count=1, flags=re.MULTILINE)
    if new_text == text:
        # field missing — insert before closing ---
        try:
            end = text.index("\n---", 3)
            new_text = text[:end] + f"\n{field}: {value}" + text[end:]
        except ValueError:
            return
    atomic_write(path, new_text)


def replace_wikilink(text: str, old_name: str, new_name: str) -> str:
    """Replace [[old_name]] with [[new_name]] everywhere in text."""
    return re.sub(
        rf"\[\[{re.escape(old_name)}\]\]",
        f"[[{new_name}]]",
        text,
    )


def remove_wikilink(text: str, name: str) -> str:
    """Remove [[name]] from connections/contradicts YAML arrays and add a deletion note."""
    # Remove array item lines like `  - "[[name]]"` or `  - [[name]]`
    text = re.sub(
        rf'^\s*-\s*"?\[\[{re.escape(name)}\]\]"?\s*\n',
        "",
        text,
        flags=re.MULTILINE,
    )
    # Remove inline occurrences like `[[name]], ` or `, [[name]]`
    text = re.sub(rf',?\s*\[\[{re.escape(name)}\]\]\s*,?', "", text)
    return text


def all_nodes(workspace: Path) -> list[Path]:
    return sorted((workspace / "02_nodes").glob("*.md"))
