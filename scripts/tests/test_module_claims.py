"""Enforce the claim a module makes about what it depends on.

"Standard library only" is a sentence several modules in scripts/ carry, and it was
false in one of them for a week: seam_contract reached markdown-it-py through
markdown_links after its heading grammar moved there, and PyYAML through
skill_interface after the constrained scalar rules gained a parser. Both arrived in
a commit that edited neither file, which is how a claim in prose goes stale — nobody
was looking at the sentence.

Transitive on purpose. A reader takes the sentence to mean the module runs without
anything installed, and reaching a third-party package through a sibling breaks that
just as thoroughly as importing it directly.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

import check_citations
from agent_skill_format import workspace_files

CLAIM = "Standard library only"
SCRIPTS = Path(__file__).resolve().parent.parent
PACKAGE = "agent_skill_format"
#: Every module a claim can be made about, by the name another module imports it under.
#: Asked of `check_citations.modules`, which owns this question for the citation gate and
#: walks the whole tree. A second glob here would have been the third answer to it, and
#: the owner's docstring records what the shape costs: a dict keyed by stem drops one of
#: two files sharing a name and says nothing, so a module's claim would go unchecked with
#: no signal. The collisions the owner returns are asserted empty below rather than
#: discarded, which is the half a private map cannot have.
_MODULES = check_citations.modules(SCRIPTS.parent)
MODULES = {
    stem: path for stem, path in _MODULES.by_stem.items() if path.stem != "__init__"
}
LOCAL = set(MODULES)
#: The modules on the package side of the boundary the carve-out is for, split from the
#: owner's map by path rather than found by a glob of the package's top directory. The
#: glob was the first form and it did not hold: a module one level down imported across
#: the boundary and the suite stayed green, because the set the assertion below subtracts
#: from never contained it. Splitting the owner's `rglob` makes the two sides complements
#: of each other, so a module cannot be absent from both.
PACKAGE_ROOT = SCRIPTS / PACKAGE
PACKAGE_MODULES = {
    stem for stem, path in MODULES.items() if path.is_relative_to(PACKAGE_ROOT)
}
STDLIB = set(sys.stdlib_module_names)


def imports(module: str) -> set[str]:
    """The names one module imports, with a package import read as the module it names.

    `from agent_skill_format.read_whole import whole` reaches a sibling, not a third
    party, and taking the first dotted segment would have called the whole package one
    installed dependency — every claim in the tree false in the same breath, which is
    louder than the silence this suite was written against but no more correct.
    """
    tree = ast.parse(MODULES[module].read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            head, _, rest = node.module.partition(".")
            if head != PACKAGE:
                found.add(head)
            elif rest:
                found.add(rest.split(".")[0])
            else:
                found |= {alias.name for alias in node.names}
    return found - {"__future__"}


def third_party(module: str, seen: set[str] | None = None) -> set[str]:
    """Every installed package this module reaches, directly or through a sibling."""
    seen = seen if seen is not None else set()
    if module in seen:
        return set()
    seen.add(module)
    found: set[str] = set()
    for name in imports(module):
        if name in LOCAL:
            found |= third_party(name, seen)
        elif name not in STDLIB:
            found.add(name)
    return found


ROOT = SCRIPTS.parent


def test_modules(root: Path) -> list[Path]:
    """Every test module this workspace carries, as git sees it.

    Not a glob on one directory. The check read `scripts/tests` alone and said so
    nowhere, so `tools/fornax-cli/tests` was outside it by accident rather than by a
    decision anybody recorded — and that suite is the one `AGENTS.md` already treats
    specially, which is exactly the kind of exclusion that needs stating if it is meant.
    `workspace_files` is the owner of "what does this workspace hold", and asking git is
    what keeps `.venv` out without a skip list that would go stale beside `.gitignore`.
    """
    files, reason = workspace_files.listed(root)
    if files is None:
        raise AssertionError(reason)
    return sorted(f for f in files if f.suffix == ".py" and f.name.startswith("test_"))


def main_guard(test: ast.expr) -> bool:
    """Whether *test* compares `__name__` against `"__main__"`, in either order.

    Matched on the tree rather than on unparsed text. One spelling was compared against
    one literal string, so `if "__main__" == __name__:` — the same construct written the
    other way round — ran `unittest.main()` while the check answered that nothing was
    there. A near-miss like `"__main_"` is refused because the literal is compared, not
    searched for.
    """
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq):
        return False
    sides = (test.left, test.comparators[0])
    names = {side.id for side in sides if isinstance(side, ast.Name)}
    literals = {side.value for side in sides if isinstance(side, ast.Constant)}
    return names == {"__name__"} and literals == {"__main__"}


def entry_point_out_of_place(source: str) -> bool:
    """Whether an entry-point block sits above anything else the module defines.

    `unittest.main()` collects the classes that exist when it runs, so a block above a
    class leaves that class uncollected on a direct run while discovery still finds it.
    The gate discovers, so it never saw this; a contributor running one file did, and so
    would a later round running the test a `docs/guards.md` row names. The measurement
    that found it is recorded under its own dated heading in that file.

    Scoped to test modules because theirs is the silent case. A script whose entry point
    calls a function defined below it raises on the spot.

    Deliberately stricter than the collection loss: a block followed by a module-level
    constant is reported and costs no test. The rule stays readable from a file's shape
    that way, and the shape is what an author can check.
    """
    body = ast.parse(source).body
    for index, node in enumerate(body):
        if isinstance(node, ast.If) and main_guard(node.test):
            return index != len(body) - 1
    return False


class ModuleClaimTests(unittest.TestCase):
    def test_every_standard_library_only_claim_is_true(self) -> None:
        # The suite is not this claim's subject and never was: taking the map from the
        # owner widened the walk, not the scan. `test_module_claims` would otherwise
        # report itself, since the string it looks for is the constant it looks with.
        claiming = sorted(
            stem
            for stem, path in MODULES.items()
            if path.parent.name != "tests" and CLAIM in path.read_text(encoding="utf-8")
        )

        self.assertTrue(claiming)
        for module in claiming:
            with self.subTest(module=module):
                self.assertEqual(third_party(module), set())

    def test_no_two_modules_share_a_name(self) -> None:
        """The half a map keyed by stem cannot hold, carried from the owner.

        Two files with one stem leave one of them unreachable through such a map, and
        every claim it makes unchecked, with nothing to say so. The owner returns the
        collisions rather than resolving them; this asserts there are none, which is
        what makes the map above safe to key that way.
        """
        self.assertEqual(_MODULES.collisions, {})

    def test_no_package_module_imports_outside_the_package(self) -> None:
        """The boundary the carve-out is for, as an assertion rather than a sentence.

        It was a sentence twice — in the commit that drew the boundary and in the one
        that widened it — and both were false. A public function in the package took a
        parameter typed by a module outside it, imported under `TYPE_CHECKING`, while
        that module imported back: a cycle across the boundary, with the repository on
        both sides of it. What verified the claim was a grep anchored at the start of a
        line, and the import is indented, so the check could not have found the thing it
        was run to find.

        `ast.walk` descends into the `TYPE_CHECKING` guard, which is what makes this
        hold the case that got through. Typing-only is not a weaker kind of edge here:
        the package is being extracted, and a signature naming a type that will not
        travel with it is an API defect at the moment of the split, not a comment.

        The first form of this assertion had the defect it was written against. It
        found the package side with a glob of one directory while the other side came
        from the owner's whole-tree walk, so a module one level down belonged to
        neither set and crossed the boundary with the suite green. Both sides come from
        the one map now and are complements, which is the property a subtraction needs
        and a pair of independent searches cannot promise.
        """
        outside = LOCAL - PACKAGE_MODULES

        for module in sorted(PACKAGE_MODULES):
            with self.subTest(module=module):
                self.assertEqual(imports(module) & outside, set())

    def test_the_check_sees_a_package_reached_through_a_sibling(self) -> None:
        # The failure that motivated this was transitive, so a direct-import check
        # would have passed the whole time.
        self.assertIn("markdown_it", third_party("markdown_links"))
        self.assertIn("markdown_it", third_party("seam_contract"))

        # And the path has to still be the transitive one for the two above to be
        # measuring transitivity at all. The assertion that stood here compared
        # "seam_contract" against `LOCAL - {"seam_contract"}` — the element the
        # subtraction removes, so it held for any tree, any import and any deletion,
        # in the one test whose name claims to see through a sibling.
        self.assertIn("markdown_links", imports("seam_contract"))
        self.assertNotIn("markdown_it", imports("seam_contract"))


class EntryPointPlacement(unittest.TestCase):
    """No test module places its entry point above something it defines.

    Stated as the shape rather than as the collection loss, which is what the check
    decides; `entry_point_out_of_place` says why the two differ.
    """

    def test_every_test_module_places_its_entry_point_last(self) -> None:
        misplaced = [
            path.name
            for path in test_modules(ROOT)
            if entry_point_out_of_place(path.read_text(encoding="utf-8"))
        ]

        self.assertEqual(misplaced, [])

    def test_the_set_reaches_every_tests_directory_the_workspace_holds(self) -> None:
        # The bound the glob left unstated: the CLI suite is a test module too.
        found = {path.parent.name for path in test_modules(ROOT)}

        self.assertIn("tests", found)
        outside_scripts = {
            path.relative_to(ROOT).parts[0] for path in test_modules(ROOT)
        } - {"scripts"}

        self.assertEqual(outside_scripts, {"tools"})

    def test_the_check_sees_an_entry_point_above_a_class(self) -> None:
        above = (
            "import unittest\n\n"
            'if __name__ == "__main__":\n    unittest.main()\n\n\n'
            "class Late(unittest.TestCase):\n    pass\n"
        )
        below = (
            "import unittest\n\n"
            "class Late(unittest.TestCase):\n    pass\n\n\n"
            'if __name__ == "__main__":\n    unittest.main()\n'
        )

        self.assertTrue(entry_point_out_of_place(above))
        self.assertFalse(entry_point_out_of_place(below))

    def test_the_check_sees_the_guard_written_the_other_way_round(self) -> None:
        # The alternate spelling of the same meaning, which a comparison against one
        # unparsed string missed while `unittest.main()` ran either way.
        reversed_guard = (
            "import unittest\n\n"
            'if "__main__" == __name__:\n    unittest.main()\n\n\n'
            "class Late(unittest.TestCase):\n    pass\n"
        )

        self.assertTrue(entry_point_out_of_place(reversed_guard))

    def test_a_near_miss_literal_is_not_an_entry_point(self) -> None:
        # The near-miss control, sharing the accepted prefix: nothing runs here.
        near_miss = (
            "import unittest\n\n"
            'if __name__ == "__main_":\n    unittest.main()\n\n\n'
            "class Late(unittest.TestCase):\n    pass\n"
        )

        self.assertFalse(entry_point_out_of_place(near_miss))

    def test_a_module_with_no_entry_point_is_not_reported(self) -> None:
        # The third answer: a module may have none, and some here do.
        self.assertFalse(entry_point_out_of_place("import unittest\n"))


if __name__ == "__main__":
    unittest.main()
