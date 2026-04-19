import io
import sys

from rich.console import Console

# On Windows the default stdout encoding is cp1252, which can't encode Unicode
# symbols like ✓ or ⚠. Wrap stdout in a UTF-8 stream so Rich outputs correctly.
# errors="replace" prevents hard crashes if a character still can't be encoded.
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    _stdout: io.TextIOBase = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
else:
    _stdout = sys.stdout  # type: ignore[assignment]

console = Console(file=_stdout, legacy_windows=False)
