#!/usr/bin/env python3
"""Check workspace text-file hygiene and repository-local Markdown links."""

from __future__ import annotations

import enum
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


class Content(enum.Enum):
    """What reading one tracked file established.

    Three answers, not two. `bytes | None` carried the file's text, a file with no bytes,
    and a read that failed — and the docstring above the return named two of the three,
    while `check` treated the last two alike, so a zero-byte file took the same silent
    path as an unresolvable one. At `v0.4.1` the empty case was an explicit `if not data:
    continue`; folding it into `return data or None` moved a policy into a truthiness
    expression and left nothing saying it was one.

    `EMPTY` is policy, not failure. A file with no bytes has no last byte to be a
    newline, and `test_an_empty_file_is_not_missing_a_newline` fixes that as the answer.
    What one `None` could not say is that this is a decision rather than a file this
    could not read.

    The shape is `skill_yaml.Shape`'s, and the reason is the one `Shape.UNREAD` and
    `path_boundary.Verdict.UNRESOLVABLE` were each added for: a state the code meant and
    the type could not name. Three states rather than a payload-or-reason pair, because
    only one of them carries bytes.
    """

    READ = "read"
    EMPTY = "empty"
    UNREADABLE = "unreadable"


@dataclass(frozen=True)
class Bytes:
    """One tracked file's bytes, or the state saying why there are none to judge."""

    state: Content
    data: bytes = b""


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
        read = _bytes(path, boundary, errors)
        if read.state is not Content.READ:
            continue

        errors.extend(_hygiene(path, read.data))
        content = _decoded(path, read.data, errors)
        if content is not None:
            errors.extend(_markdown_links(path, content, boundary))
    return errors


def _bytes(path: Path, boundary: Boundary, errors: list[Diagnostic]) -> Bytes:
    """The file's bytes, the fact that it has none, or that they could not be read.

    Each of the three is named rather than shared. Whatever stopped a read is reported
    here as it happens; `EMPTY` reports nothing, because having no bytes is not a defect
    and `Content` is where that is written down instead of in a truthiness test.
    """
    tracked = resolve_within(path, boundary)
    if tracked.verdict is Verdict.UNRESOLVABLE:
        errors.append(Diagnostic(path, f"tracked path could not be resolved: {tracked.error}"))
        return Bytes(Content.UNREADABLE)
    if tracked.verdict is Verdict.OUTSIDE:
        errors.append(Diagnostic(path, "tracked path leaves repository"))
        return Bytes(Content.UNREADABLE)
    if tracked.verdict is Verdict.ABSENT:
        # git already reports the deletion, and there is no text to read
        return Bytes(Content.UNREADABLE)
    if not path.is_file():
        return Bytes(Content.UNREADABLE)
    try:
        data = path.read_bytes()
    except OSError as error:
        errors.append(Diagnostic(path, str(error)))
        return Bytes(Content.UNREADABLE)
    return Bytes(Content.READ, data) if data else Bytes(Content.EMPTY)


def _hygiene(path: Path, data: bytes) -> list[Diagnostic]:
    """Whether the bytes are text at all, and whether they end as text should.

    Every tracked file, because this repository tracks no binary one: `git grep -I`
    finds nothing binary among its tracked files, and the policy in AGENTS.md is that
    adding one is a deliberate change to this check rather than a file it passes over.

    Passing over a NUL was written for a binary file that does not exist here and it
    exempted the files that do. A `.md` holding a NUL was reported and a `.py` or a
    `.yaml` holding one was reported by nothing at all — the same shape as `_decoded`
    reading `.md` alone, in the function beside it, left standing when that was
    repaired because the sweep read the diff instead of the mechanism.
    """
    if b"\0" in data:
        return [Diagnostic(path, "tracked file must be text")]
    if not data.endswith(b"\n"):
        return [Diagnostic(path, "text file must end with a newline")]
    return []


def _decoded(path: Path, data: bytes, errors: list[Diagnostic]) -> str | None:
    """The text of any tracked text file, or a report that it is not readable as text.

    Every suffix, not only `.md`. `check_sources` and `distribution_manifest` both skip
    a file they cannot read under a comment saying text hygiene owns it, and both
    deferrals were correct only if this actually read the file. It read `.md` alone, so
    a tracked `.yaml` holding invalid UTF-8 was reported by nothing, and the gate said
    the same thing whether it had parsed the file or never opened it.

    The first version of this paragraph named `evidence_currency`, which does not defer
    here at all, and omitted `distribution_manifest`, which does — a docstring listing
    its own callers from memory, wrong in both directions on the day it was written.
    `grep "text hygiene" scripts/` is what settles it.
    """
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(Diagnostic(path, "text file must use UTF-8"))
        return None


def _markdown_links(path: Path, content: str, boundary: Boundary) -> list[Diagnostic]:
    """Every repository-local Markdown link that does not resolve inside the tree.

    Which files have links is this policy's own question. Widening `_decoded` to every
    suffix left its `.md` test with no home and it went up into `check`, whose docstring
    says judging is not its job — and whose split exists to stop it holding a list of
    policies.
    """
    if path.suffix.lower() != ".md":
        return []
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
