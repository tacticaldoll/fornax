#!/usr/bin/env python3
"""Parse the non-Python sources this environment can parse.

Ruff covers the Python. The repository also ships a shell hook and a JavaScript
plugin, and a syntax error in either is found by whoever runs it rather than by a
gate. Only the shell hook is checked here: `bash` is present wherever this gate
runs, while `node` is not declared by the maintenance environment, so the plugin
stays a CI step until it is.

A missing interpreter is a failure, not a skip. Silently passing would make this
gate report the same result whether it parsed the file or never opened it.

Standard library only.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from diagnostic_text import printable


ROOT = Path(__file__).resolve().parent.parent
PARSERS = ((".githooks/pre-commit", ("bash", "-n")),)


def check(root: Path) -> list[str]:
    """Return one diagnostic per source that does not parse or cannot be parsed."""
    errors: list[str] = []
    for relative_path, command in PARSERS:
        path = root / relative_path
        if not path.is_file():
            errors.append(f"{relative_path} is missing")
            continue
        if shutil.which(command[0]) is None:
            errors.append(f"{relative_path} needs {command[0]}, which is not on PATH")
            continue
        result = subprocess.run(
            [*command, str(path)], capture_output=True, text=True, check=False
        )
        if result.returncode:
            errors.append(f"{relative_path} does not parse: {result.stderr.strip()}")
    return errors


def main() -> int:
    errors = check(ROOT)
    for error in errors:
        print(printable(f"FAIL non-Python sources - {error}"))
    if errors:
        return 1
    print(printable(f"OK   non-Python sources ({len(PARSERS)} parsed)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
