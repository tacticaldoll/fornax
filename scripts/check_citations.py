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

Where that verification stops: a citation into this tree is checked to its symbol and to
a class member below it, and a citation naming an external module is checked only to the
module. Reading an external symbol means reading source this repository does not hold —
the standard library's by an interpreter path, a package's by whatever a local
environment installed — and the second of those is the environment dependence this check
was just repaired for. No external symbol has ever been miscited here, so the reading is
not bought; what is bought is that a module name outside `scripts/`, the standard library
and this repository's own imports is refused, which is what a mistyped internal module
looks like. `development-knowns.yaml` records the gap.

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
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from diagnostic_text import printable
from markdown_links import prose_lines

ROOT = Path(__file__).resolve().parent.parent

SUBJECTS = ("AGENTS.md", "PROJECT.md", "README.md", "development-knowns.yaml", "docs/guards.md")
RECORDS = Path("docs/dispositions")

# Suffixes a citation may name, used only to tell a filename from a symbol citation.
SOURCE_SUFFIXES = ("py", "md", "yaml", "yml", "toml", "txt", "json", "js", "sh", "cfg")

# Any path with an alphabetic extension, backticks or not, and no cap on the extension's
# length — capped at six it passed `.markdown`. The extension must be letters, or a
# version and a column read as a citation. A match inside a URL's authority is not one:
# `https://example.com:443/path` yields `//example.com:443`, so the whole whitespace-
# bounded word is examined and a word carrying a scheme separator is left alone.
LINE_CITATION = re.compile(r"[A-Za-z0-9_./-]+\.[A-Za-z][A-Za-z0-9]*:\d+(?:-\d+)?")
# Only a URL's authority is exempt. Skipping the whole whitespace-bounded word let a
# citation inside a URL's path escape as well, and a path there is as much a path as
# anywhere. The authority runs to the next slash, from the scheme separator or — for a
# network-path reference, which carries an authority and no scheme — from the leading
# pair of slashes. `markdown_links.local_target` already reads that second form as a
# destination this repository does not own, so recognising one form and not the other was
# this module disagreeing with the module that owns the grammar.
URL_AUTHORITY = re.compile(r"://[^/\s]*|(?<![:\w./-])//[^/\s]*")
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


@dataclass
class Modules:
    """The module map, and the stems that name more than one file.

    A dict keyed by stem answered the wrong question silently: two files sharing a stem
    left one of them unreachable, and a citation into the shadowed one was checked
    against the other. So the collision is a value here rather than a lost key, and the
    caller reports it instead of resolving it — which file a bare stem means is a
    question the citation form cannot answer, so the form has to change or the files do.
    """

    by_stem: dict[str, Path]
    collisions: dict[str, list[Path]]
    #: What each module defines, parsed once and kept for the run. A citation names a
    #: module as often as it is cited, and every one re-read and re-parsed the file.
    read: dict[str, "Symbols"] = field(default_factory=dict)


def modules(root: Path) -> Modules:
    """Every module under `scripts/`, by the name a citation would use.

    `scripts/tests/` included. Reading only the top directory made every citation into a
    test module — and a Reach entry naming a test is the ordinary case — an unknown
    module, reported against its production sibling.
    """
    scripts = root / "scripts"
    if not scripts.is_dir():
        return Modules({}, {})
    found: dict[str, list[Path]] = {}
    for path in sorted(scripts.rglob("*.py")):
        found.setdefault(path.stem, []).append(path)
    return Modules(
        {stem: paths[0] for stem, paths in found.items()},
        {stem: paths for stem, paths in found.items() if len(paths) > 1},
    )


@dataclass(frozen=True)
class Symbols:
    """What a module defines, or why this could not say — never both, and never neither.

    Three states shared one `None` before: no such module, a module that would not read,
    and a module that would not parse. The caller reported all three as "names no module
    here", so an unreadable module read as a citation defect and the real failure was
    invisible. The shape is `skill_yaml.Document`'s, for the same reason.
    """

    _names: dict[str, set[str]] | None
    reason: str | None
    #: The top-level module names this module imports, for `citable`. Collected in the
    #: same pass: both questions read the same file, and reading it twice let the two
    #: answers disagree about what an unreadable module means. Private for the reason
    #: the payload above is — an unreadable module answered a public `imports` with a
    #: confident empty set, which reads as "imports nothing" where the truth is "could
    #: not be read", and that is the swallow this field's own commit removed.
    _imports: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if (self._names is None) == (self.reason is None):
            raise ValueError("symbols hold a mapping or a reason, never both or neither")

    @property
    def names(self) -> dict[str, set[str]]:
        if self._names is None:
            raise ValueError(self.reason or "")
        return self._names

    @property
    def imports(self) -> frozenset[str]:
        if self._names is None:
            raise ValueError(self.reason or "")
        return self._imports


def module_symbols(known: Modules, module: str) -> Symbols | None:
    """What a `scripts/` module defines at its top level, each with its own members.

    None for no such module, which is not a defect on its own — a citation whose first
    part is not a module here may be an installed one, and the caller decides. A module
    that exists and cannot be read or parsed comes back as a reason, because that is a
    failure to report rather than a citation to judge.

    Members are carried because a class member is the natural unit to cite for one, and
    a citation this cannot follow is a citation this does not check. A wrong method name
    in a cell asserting a closure was verified is the defect that prompted the rule.

    The map is handed in rather than re-derived. It used to take a root and rebuild the
    map for every symbol citation, while both callers above it were already holding one,
    so a run walked the `scripts/` tree once per citation and re-parsed each cited module
    every time it was named.
    """
    path = known.by_stem.get(module)
    if path is None:
        return None
    if module in known.read:
        return known.read[module]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except OSError as error:
        known.read[module] = Symbols(None, f"could not be read: {error}")
        return known.read[module]
    except SyntaxError as error:
        known.read[module] = Symbols(None, f"could not be parsed: {error}")
        return known.read[module]
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            imported.add(node.module.split(".")[0])
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
    known.read[module] = Symbols(names, None, frozenset(imported))
    return known.read[module]


def citable(known: Modules) -> set[str]:
    """Every module name a citation may name without this tree defining it.

    Derived, not asked of the environment. `find_spec` stood here first, which made the
    answer depend on what happened to be installed in the interpreter running the check
    rather than on anything this repository declares. The stdlib set is static and comes
    with the interpreter version `.python-version` pins; the third-party names are the
    ones some module under `scripts/` actually imports, read from the import statements.

    Read through `module_symbols` rather than by a second walk of the same tree. The two
    passes parsed the same files for different questions and disagreed about failure:
    this one swallowed an unparseable module and the other reported it, so one run could
    call the same file absent and defective. Now a module that will not parse holds its
    reason once, contributes no imports, and is reported wherever it is cited.

    So a name outside all of this — `scripts/`, the standard library, and what this
    repository imports — resolves nowhere that matters, whatever a local environment
    holds. A similarity heuristic stood here before `find_spec` and passed every
    misspelling unlike enough to a real name, which was the same silence in a smaller
    range.
    """
    names = set(sys.stdlib_module_names)
    for module in known.by_stem:
        symbols = module_symbols(known, module)
        if symbols is not None and symbols.reason is None:
            names.update(symbols.imports)
    return names


def citations(known: Modules, root: Path, path: Path, external: set[str]) -> list[Diagnostic]:
    """Every citation in one file that names a line, or a symbol nothing defines."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []  # text hygiene owns unreadable files and reports them there

    lines = prose_lines(text) if path.suffix == ".md" else list(enumerate(text.splitlines(), 1))
    found: list[Diagnostic] = []
    for number, line in lines:
        urls = [found.span() for found in URL_AUTHORITY.finditer(line)]
        for match in LINE_CITATION.finditer(line):
            if any(start <= match.start() and match.end() <= end for start, end in urls):
                continue  # a host and a port in a URL's authority, not a path and a line
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
            symbols = module_symbols(known, module)
            if symbols is None:
                if module not in external:
                    found.append(
                        Diagnostic(
                            path,
                            number,
                            f"{match.group(0)} names a module that is not under "
                            "scripts/, not in the standard library, and not imported "
                            "anywhere here",
                        )
                    )
                continue
            if symbols.reason is not None:
                found.append(
                    Diagnostic(
                        path,
                        number,
                        f"{known.by_stem[module].relative_to(root)} {symbols.reason}"
                        f", so {match.group(0)} could not be checked",
                    )
                )
                continue
            where = known.by_stem[module].relative_to(root)
            if parts[0] not in symbols.names:
                found.append(
                    Diagnostic(
                        path,
                        number,
                        f"{match.group(0)} names no top-level symbol in {where}",
                    )
                )
            elif len(parts) > 1 and parts[1] not in symbols.names[parts[0]]:
                found.append(
                    Diagnostic(
                        path,
                        number,
                        f"{match.group(0)} names no member of {parts[0]} in {where}",
                    )
                )
    return found


def check(root: Path) -> list[Diagnostic]:
    """Every citation defect across the subject files, and any module name that is not one.

    A stem naming more than one file is reported once, against the repository rather than
    against a document: no citation in any subject is wrong for it, and every citation
    naming that stem is unverifiable until the ambiguity goes.
    """
    known = modules(root)
    found = [
        Diagnostic(
            root,
            0,
            f"`{stem}` names more than one module — "
            + ", ".join(str(path.relative_to(root)) for path in paths)
            + " — so a citation naming it cannot be checked",
        )
        for stem, paths in sorted(known.collisions.items())
    ]
    external = citable(known)
    return found + [
        problem
        for path in subjects(root)
        for problem in citations(known, root, path, external)
    ]


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
