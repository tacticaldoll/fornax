"""Enforce the claim a module makes about what it depends on.

"Standard library only" is a sentence nine modules in scripts/ carry, and it was
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
        self.assertNotIn("seam_contract", LOCAL - {"seam_contract"})
