#!/usr/bin/env python3
"""Check that this repository's durable reasoning cites something that survives an edit.

A `path:line` citation is keyed to a coordinate that moves with the next edit to that
file. It can only be maintained by hand, and it fails quietly: a review round found wrong
symbols and wrong lines inside the cells asserting that closures had been verified, and
the citations that had gone unverifiable were the ones whose files had changed since their
record landed. The measurement is in the dated record for that round.

So the citation form is what this refuses, and the symbol form is what it verifies. A
line number cannot be checked without knowing what it was meant to point at; a symbol
can, and a symbol that no longer exists is the defect a wrong line number hides.

What this costs, stated because it is the objection to the rule it enforces: renaming a
cited symbol turns every record citing it red. That is not the failure mode a line
number has. A line number breaks on any edit anywhere above it, silently and with no
correct answer available; a renamed symbol breaks exactly when a record's claim stops
being locatable, and the correct answer is the new name. The repository's own rule for
keying a finding says to preserve the logical unit when code moves, so a rename is
already an occasion to touch the records that name it.

The subject is what this repository authors as durable reasoning, listed in SUBJECTS.
Two things are outside it, and not by exemption: a Review Record's evidence column is a
coordinate into the tree as reviewed and is read once, and raw scores under
`scripts/tests/scenarios/` quote what an agent produced during a run, where an edit
falsifies the record. Anything inside a fenced block is a quotation too, which is why
lines come from `markdown_links.prose_lines` rather than from `splitlines`.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from diagnostic_text import printable
from markdown_links import prose_lines

ROOT = Path(__file__).resolve().parent.parent

SUBJECTS = ("AGENTS.md", "PROJECT.md", "README.md", "development-knowns.yaml")
RECORDS = Path("docs/dispositions")

SOURCE_SUFFIXES = ("py", "md", "yaml", "yml", "toml", "txt", "json", "js", "sh", "cfg")
# Any path with an alphabetic extension, backticks or not. The first form of this asked
# for backticks and a suffix from the list above, so `scripts/foo.py:12` in plain prose
# and a `.js` citation both passed a check whose message says the form is refused. The
# extension must be letters, or `Python 3.10:1` reads as a citation.
LINE_CITATION = re.compile(r"[A-Za-z0-9_./-]+\.[A-Za-z]{1,6}:\d+(?:-\d+)?")
SYMBOL_CITATION = re.compile(
    r"`([a-z][a-z0-9_]*)((?:\.[A-Za-z_][A-Za-z0-9_]*){1,2})`"
)


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    line: int
    message: str


def subjects(root: Path) -> list[Path]:
    """Every file whose citations this checks, in a stable order."""
    found = [root / name for name in SUBJECTS if (root / name).is_file()]
    records = root / RECORDS
    if records.is_dir():
        found.extend(sorted(records.glob("*.md")))
    return found


def modules(root: Path) -> dict[str, Path]:
    """Every module under `scripts/`, by the name a citation would use.

    `scripts/tests/` included. Reading only the top directory made every citation into a
    test module — and a Reach entry naming a test is the ordinary case — an unknown
    module that the near-miss rule below then reported against its production sibling:
    `test_validate_skills.check` came back as a misspelling of `validate_skills`.
    """
    scripts = root / "scripts"
    if not scripts.is_dir():
        return {}
    return {path.stem: path for path in sorted(scripts.rglob("*.py"))}


def module_symbols(root: Path, module: str) -> dict[str, set[str]] | None:
    """What a `scripts/` module defines at its top level, each with its own members.

    None rather than an empty mapping: a citation whose first part is not a module here
    — a standard-library call, a dotted filename — is not a claim about this tree, and
    the caller must be able to tell that from a module that defines nothing.

    Members are carried because a class member is the natural unit to cite for one, and
    a citation this cannot follow is a citation this does not check. `Document.require`
    is exactly the shape of the wrong-symbol defect that prompted the rule.
    """
    path = modules(root).get(module)
    if path is None:
        return None
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    names: dict[str, set[str]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names[node.name] = set()
        elif isinstance(node, ast.ClassDef):
            members = set()
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    members.add(child.name)
                elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                    members.add(child.target.id)
                elif isinstance(child, ast.Assign):
                    members.update(t.id for t in child.targets if isinstance(t, ast.Name))
            names[node.name] = members
        elif isinstance(node, ast.Assign):
            names.update({t.id: set() for t in node.targets if isinstance(t, ast.Name)})
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names[node.target.id] = set()
    return names


def citations(root: Path, path: Path) -> list[Diagnostic]:
    """Every citation in one file that names a line, or a symbol its module does not define."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []  # text hygiene owns unreadable files and reports them there

    lines = prose_lines(text) if path.suffix == ".md" else list(enumerate(text.splitlines(), 1))
    found: list[Diagnostic] = []
    for number, line in lines:
        for match in LINE_CITATION.finditer(line):
            found.append(
                Diagnostic(
                    path,
                    number,
                    f"{match.group(0)} cites a line; cite the file and a symbol or a "
                    "quoted phrase, which survive an edit",
                )
            )
        for match in SYMBOL_CITATION.finditer(line):
            module, rest = match.groups()
            parts = rest.lstrip(".").split(".")
            if parts[0] in SOURCE_SUFFIXES:
                continue  # `evidence_currency.py` is a filename, not a symbol citation
            names = module_symbols(root, module)
            if names is None:
                # An unknown module is either something outside this tree or a
                # misspelling of something inside it, and the first version of this
                # check read both as the first — so `evidnce_currency.resolved_inside`
                # passed silently, which is the whole failure a citation check exists to
                # stop. A misspelling is a near-miss by definition, so that is what
                # separates them, with no list of external modules to maintain.
                near = difflib.get_close_matches(module, list(modules(root)), n=1, cutoff=0.8)
                if near:
                    found.append(
                        Diagnostic(
                            path,
                            number,
                            f"{match.group(0)} names no module here; "
                            f"{modules(root)[near[0]].relative_to(root)} is one character-set away",
                        )
                    )
                continue
            if parts[0] not in names:
                found.append(
                    Diagnostic(
                        path,
                        number,
                        f"{match.group(0)} names no top-level symbol in "
                        f"{modules(root)[module].relative_to(root)}",
                    )
                )
            elif len(parts) > 1 and parts[1] not in names[parts[0]]:
                found.append(
                    Diagnostic(
                        path,
                        number,
                        f"{match.group(0)} names no member of {parts[0]} in "
                        f"{modules(root)[module].relative_to(root)}",
                    )
                )
    return found


def check(root: Path) -> list[Diagnostic]:
    """Every citation defect across the subject files."""
    return [problem for path in subjects(root) for problem in citations(root, path)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="Repository root to check.")
    args = parser.parse_args(argv)
    root = Path(args.root) if args.root else ROOT

    problems = check(root)
    for problem in problems:
        where = problem.path
        if where.is_relative_to(root):
            where = where.relative_to(root)
        print(printable(f"FAIL {where}:{problem.line} - {problem.message}"), file=sys.stderr)
    if problems:
        return 1
    print(printable(f"OK   citations in {len(subjects(root))} document(s)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
