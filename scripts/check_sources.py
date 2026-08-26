#!/usr/bin/env python3
"""Parse the non-Python sources this environment can parse.

Ruff covers the Python. The repository also ships a shell hook, a JavaScript plugin
and every tracked YAML file, and a syntax error in any of them is found by whoever
runs it rather than by a gate. The hook and the YAML are checked here; `node` is not
declared by the maintenance environment, so the plugin stays a CI step until it is.

The YAML is checked because a `.yaml` extension is a claim, and this repository's own
registries did not meet it: both carried a plain scalar holding ": ", which YAML
forbids, so no parser could read either while the readers written for them could.
Nothing could see that, because nothing had ever asked a YAML parser to read them.
Now something does, on every commit.

A missing interpreter is a failure, not a skip. Silently passing would make this
gate report the same result whether it parsed the file or never opened it.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml

from diagnostic_text import printable
from workspace_files import listed


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

    documents, error = yaml_documents(root)
    if error is not None:
        errors.append(error)
    else:
        errors.extend(documents)
    return errors


def yaml_documents(root: Path) -> tuple[list[str], str | None]:
    """One diagnostic per tracked YAML file a YAML parser cannot read.

    Derived from the workspace rather than listed, so a registry added where nobody
    thought to register it is read like the rest.
    """
    paths, error = listed(root)
    if error is not None:
        return [], error

    errors: list[str] = []
    for path in sorted(paths):
        if path.suffix not in (".yaml", ".yml") or not path.is_file():
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            continue  # text hygiene owns unreadable files and reports them there
        except yaml.YAMLError as failure:
            reason = str(failure).replace("\n", " ")
            errors.append(f"{path.relative_to(root).as_posix()} is not YAML: {reason}")
    return errors, None


def main() -> int:
    errors = check(ROOT)
    for error in errors:
        print(printable(f"FAIL non-Python sources - {error}"))
    if errors:
        return 1
    print(printable("OK   non-Python sources"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
