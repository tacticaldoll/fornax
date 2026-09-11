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

import workspace_files

CLAIM = "Standard library only"
SCRIPTS = Path(__file__).resolve().parent.parent
LOCAL = {path.stem for path in SCRIPTS.glob("*.py")}
STDLIB = set(sys.stdlib_module_names)


def imports(module: str) -> set[str]:
    tree = ast.parse((SCRIPTS / f"{module}.py").read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split(".")[0])
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
        claiming = sorted(
            path.stem
            for path in SCRIPTS.glob("*.py")
            if CLAIM in path.read_text(encoding="utf-8")
        )

        self.assertTrue(claiming)
        for module in claiming:
            with self.subTest(module=module):
                self.assertEqual(third_party(module), set())

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
