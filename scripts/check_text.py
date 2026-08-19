#!/usr/bin/env python3
"""Check workspace text-file hygiene and repository-local Markdown links."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from markdown_links import iter_markdown_links, local_target


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    message: str


def workspace_files(root: Path) -> list[Path]:
    """Return cached and non-ignored untracked files in the workspace."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [root / os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def check(files: list[Path]) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    for path in files:
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            errors.append(Diagnostic(path, str(error)))
            continue
        if not data or b"\0" in data:
            continue
        if not data.endswith(b"\n"):
            errors.append(Diagnostic(path, "text file must end with a newline"))
        if path.suffix.lower() != ".md":
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for link in iter_markdown_links(content):
            target = local_target(link.destination)
            if target is None:
                continue
            if Path(target).is_absolute():
                errors.append(
                    Diagnostic(path, f"absolute Markdown link is not allowed: {link.shown_target}")
                )
                continue
            if not (path.parent / target).exists():
                errors.append(Diagnostic(path, f"link not found: {link.shown_target}"))
    return errors


def main() -> int:
    try:
        errors = check(workspace_files(ROOT))
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"FAIL text hygiene - {error}")
        return 1
    for error in errors:
        try:
            shown = error.path.relative_to(ROOT)
        except ValueError:
            shown = error.path
        print(f"FAIL {shown}: {error.message}")
    if errors:
        return 1
    print("OK   workspace text hygiene and local Markdown links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
