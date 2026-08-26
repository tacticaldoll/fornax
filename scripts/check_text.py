#!/usr/bin/env python3
"""Check workspace text-file hygiene, repository-local Markdown links, and written counts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from diagnostic_text import printable
from host_paths import is_absolute_anywhere
from markdown_links import iter_markdown_links, local_target
from path_boundary import Boundary, Verdict, resolve_within
from workspace_files import listed


ROOT = Path(__file__).resolve().parent.parent

# Nouns naming something the repository contains. A number written next to one of
# these is a claim about the tree that nothing reads, and each of these nouns has
# carried a stale one: README named fewer gate steps than ran, generated_block named
# fewer consumers than dispatched blocks, PROJECT.md kept seam counts by hand.
#
# A pre-filter, not the rule. It sees a number standing immediately before one of
# these nouns, which is the plainest form and the one every stale count here had
# taken; a count with a word in between, or beside a noun not listed, passes. The rule
# is an authoring judgment and AGENTS.md states it as one — the sweep that removed
# these was done by reading, and this caught the plainest of them.
INVENTORY = (
    "arms|cases|checks|commits|consumers|controls|copies|entries|families|files|findings|"
    "forms|generators|grammars|knowns|layers|matchers|modules|readers|rounds|seams|skills|"
    "steps|tests|ways"
)
COUNTED = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
    r"fourteen|fifteen|twenty|twenty-two)[ \t]+(?:" + INVENTORY + r")\b",
    re.IGNORECASE,
)
# Where a number beside one of those nouns is not a claim about the tree: a skill
# states rules and thresholds, and a scenario record states the parameters a measured
# result was taken under, which cannot be reworded without falsifying the record.
COUNT_FREE = ("skills/", "scripts/tests/scenarios/", "docs/dispositions/")
COUNTED_SUFFIXES = (".md", ".py", ".yaml", ".yml", ".toml")


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    message: str


def check(files: list[Path], root: Path) -> list[Diagnostic]:
    """Read each tracked file once and hand its bytes to the policies that judge them.

    Reading is this function's job; judging is not. It owned path containment, file
    reads, encoding and newline policy, the written-count pre-filter and Markdown link
    resolution in one body, and a body whose job takes four clauses to state is a body
    nobody can review one clause at a time.
    """
    errors: list[Diagnostic] = []
    boundary = Boundary.at(root)
    for path in files:
        data = _bytes(path, boundary, errors)
        if data is None:
            continue

        errors.extend(_hygiene(path, data))
        content = _decoded(path, data, errors)
        if content is None:
            continue

        errors.extend(_written_counts(path, path.relative_to(root).as_posix(), content))
        if path.suffix.lower() == ".md":
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
    """The text, for the suffixes whose contents are judged below."""
    if b"\0" in data or path.suffix.lower() not in COUNTED_SUFFIXES:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        if path.suffix.lower() == ".md":
            errors.append(Diagnostic(path, "Markdown file must use UTF-8"))
        return None


def _written_counts(path: Path, relative: str, content: str) -> list[Diagnostic]:
    """The plainest written counts, which is all this pre-filter claims to see."""
    if relative.startswith(COUNT_FREE):
        return []
    found = []
    for line, text in enumerate(content.splitlines(), 1):
        counted = COUNTED.search(text)
        if counted:
            found.append(Diagnostic(path, f"line {line} writes a count: {counted.group(0)}"))
    return found


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
    print("OK   workspace text hygiene, local Markdown links, and plainly written counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
