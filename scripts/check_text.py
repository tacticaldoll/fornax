#!/usr/bin/env python3
"""Check tracked text-file hygiene and repository-local Markdown links."""

from __future__ import annotations

import re
import subprocess
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [root / os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def local_target(raw: str) -> str | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
        return None
    return target


def check(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            errors.append(f"{path}: {error}")
            continue
        if not data or b"\0" in data:
            continue
        if not data.endswith(b"\n"):
            errors.append(f"{path}: text file must end with a newline")
        if path.suffix.lower() != ".md":
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for raw in MARKDOWN_LINK.findall(content):
            target = local_target(raw)
            if target is None or Path(target).is_absolute():
                continue
            if not (path.parent / target).exists():
                errors.append(f"{path}: link not found: {raw}")
    return errors


def main() -> int:
    try:
        errors = check(tracked_files(ROOT))
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"FAIL text hygiene - {error}")
        return 1
    for error in errors:
        absolute = error.split(":", 1)[0]
        try:
            shown = Path(absolute).relative_to(ROOT)
            error = str(shown) + error[len(absolute) :]
        except ValueError:
            pass
        print(f"FAIL {error}")
    if errors:
        return 1
    print("OK   tracked text hygiene and local Markdown links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
