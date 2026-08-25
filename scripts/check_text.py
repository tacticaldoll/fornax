#!/usr/bin/env python3
"""Check workspace text-file hygiene and repository-local Markdown links."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from diagnostic_text import printable
from host_paths import is_absolute_anywhere
from markdown_links import iter_markdown_links, local_target
from path_boundary import Boundary, Verdict, resolve_within
from workspace_files import listed, workspace_files  # noqa: F401  (re-export: the suite reads it here)


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    message: str


def check(files: list[Path], root: Path) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    boundary = Boundary.at(root)
    for path in files:
        tracked = resolve_within(path, boundary)
        if tracked.verdict is Verdict.UNRESOLVABLE:
            errors.append(
                Diagnostic(path, f"tracked path could not be resolved: {tracked.error}")
            )
            continue
        if tracked.verdict is Verdict.OUTSIDE:
            errors.append(Diagnostic(path, "tracked path leaves repository"))
            continue
        if tracked.verdict is Verdict.ABSENT:
            continue  # git already reports the deletion, and there is no text to read
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            errors.append(Diagnostic(path, str(error)))
            continue
        if not data:
            continue
        if b"\0" in data:
            # A binary file is not this check's subject, but a .md holding a NUL is
            # a Markdown file that is not text, and skipping it in silence hid every
            # link in it. Invalid UTF-8 in a .md is already reported below.
            if path.suffix.lower() == ".md":
                errors.append(Diagnostic(path, "Markdown file must be text"))
            continue
        if not data.endswith(b"\n"):
            errors.append(Diagnostic(path, "text file must end with a newline"))
        if path.suffix.lower() != ".md":
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(Diagnostic(path, "Markdown file must use UTF-8"))
            continue
        for link in iter_markdown_links(content):
            target = local_target(link.destination)
            if target is None:
                continue
            if is_absolute_anywhere(target):
                errors.append(
                    Diagnostic(path, f"absolute Markdown link is not allowed: {link.shown_target}")
                )
                continue
            found = resolve_within(path.parent / target, boundary)
            if found.verdict is Verdict.UNRESOLVABLE:
                errors.append(
                    Diagnostic(
                        path,
                        f"link could not be resolved: {link.shown_target} ({found.error})",
                    )
                )
            elif found.verdict is Verdict.OUTSIDE:
                errors.append(Diagnostic(path, f"link leaves repository: {link.shown_target}"))
            elif found.verdict is Verdict.ABSENT:
                errors.append(Diagnostic(path, f"link not found: {link.shown_target}"))
    return errors


def main() -> int:
    paths, error = listed(ROOT)
    if error is not None:
        print(printable(f"FAIL text hygiene - {error}"))
        return 1
    errors = check(paths, ROOT)
    for error in errors:
        try:
            shown = error.path.relative_to(ROOT)
        except ValueError:
            shown = error.path
        print(printable(f"FAIL {shown}: {error.message}"))
    if errors:
        return 1
    print("OK   workspace text hygiene and local Markdown links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
