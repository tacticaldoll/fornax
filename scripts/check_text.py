#!/usr/bin/env python3
"""Check workspace text-file hygiene and repository-local Markdown links."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from diagnostic_text import printable
from host_paths import is_absolute_anywhere
from markdown_links import iter_markdown_links, local_target
from path_boundary import Boundary, Verdict, resolve_within
from workspace_files import listed


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    message: str


def check(files: list[Path], root: Path) -> list[Diagnostic]:
    """Read each tracked file once and hand its bytes to the policies that judge them.

    Reading is this function's job; judging is not. It owned path containment, file
    reads, encoding and newline policy and Markdown link resolution in one body, and a
    body whose job takes a list of clauses to state is a body nobody can review one
    clause at a time.
    """
    errors: list[Diagnostic] = []
    boundary = Boundary.at(root)
    for path in files:
        data = _bytes(path, boundary, errors)
        if data is None:
            continue

        errors.extend(_hygiene(path, data))
        content = _decoded(path, data, errors)
        if content is not None:
            errors.extend(_markdown_links(path, content, boundary))
    return errors


def _bytes(path: Path, boundary: Boundary, errors: list[Diagnostic]) -> bytes | None:
    """The file's bytes, or nothing plus whatever stopped this from reading them."""
    tracked = resolve_within(path, boundary)
    if tracked.verdict is Verdict.UNRESOLVABLE:
        errors.append(Diagnostic(path, f"tracked path could not be resolved: {tracked.error}"))
        return None
    if tracked.verdict is Verdict.OUTSIDE:
        errors.append(Diagnostic(path, "tracked path leaves repository"))
        return None
    if tracked.verdict is Verdict.ABSENT:
        return None  # git already reports the deletion, and there is no text to read
    if not path.is_file():
        return None
    try:
        data = path.read_bytes()
    except OSError as error:
        errors.append(Diagnostic(path, str(error)))
        return None
    return data or None


def _hygiene(path: Path, data: bytes) -> list[Diagnostic]:
    """Whether the bytes are text at all, and whether they end as text should."""
    if b"\0" in data:
        # A binary file is not this check's subject, but a .md holding a NUL is a
        # Markdown file that is not text, and skipping it in silence hid every link in
        # it. Invalid UTF-8 in a .md is reported by the decode below.
        if path.suffix.lower() == ".md":
            return [Diagnostic(path, "Markdown file must be text")]
        return []
    if not data.endswith(b"\n"):
        return [Diagnostic(path, "text file must end with a newline")]
    return []


def _decoded(path: Path, data: bytes, errors: list[Diagnostic]) -> str | None:
    """The Markdown text whose links are resolved below."""
    if b"\0" in data or path.suffix.lower() != ".md":
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(Diagnostic(path, "Markdown file must use UTF-8"))
        return None


def _markdown_links(path: Path, content: str, boundary: Boundary) -> list[Diagnostic]:
    """Every repository-local Markdown link that does not resolve inside the tree."""
    errors: list[Diagnostic] = []
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
                Diagnostic(path, f"link could not be resolved: {link.shown_target} ({found.error})")
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
