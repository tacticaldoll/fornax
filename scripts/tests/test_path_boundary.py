from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from path_boundary import Boundary, Verdict, resolve_within


class PathBoundaryTests(unittest.TestCase):
    def test_a_resolvable_path_inside_the_boundary_is_inside(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "present.md"
            target.write_text("x\n", encoding="utf-8")

            found = resolve_within(target, Boundary.at(root))

        self.assertIs(found.verdict, Verdict.INSIDE)

    def test_a_path_outside_the_boundary_is_outside(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            outside = parent / "outside.md"
            outside.write_text("x\n", encoding="utf-8")

            found = resolve_within(outside, Boundary.at(root))

        self.assertIs(found.verdict, Verdict.OUTSIDE)

    def test_an_escaping_symlink_to_a_missing_target_is_outside_not_absent(self) -> None:
        # Containment outranks existence: a path that both escapes and is missing is
        # an escape. Reporting it as "not found" would name the wrong problem.
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            alias = root / "alias.md"
            alias.symlink_to(parent / "never-created.md")

            found = resolve_within(alias, Boundary.at(root))

        self.assertIs(found.verdict, Verdict.OUTSIDE)

    def test_a_missing_path_inside_the_boundary_is_absent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            found = resolve_within(root / "never-created.md", Boundary.at(root))

        self.assertIs(found.verdict, Verdict.ABSENT)

    def test_a_symlink_pointing_inside_at_nothing_is_absent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            alias = root / "alias.md"
            alias.symlink_to("gone.md")

            found = resolve_within(alias, Boundary.at(root))

        self.assertIs(found.verdict, Verdict.ABSENT)

    def test_an_embedded_null_byte_is_unresolvable_not_an_exception(self) -> None:
        # A Markdown link holding %00 decodes to this, and resolving it used to raise
        # ValueError out of the text check instead of being reported.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            found = resolve_within(root / "a\x00b.md", Boundary.at(root))

        self.assertIs(found.verdict, Verdict.UNRESOLVABLE)
        self.assertIsInstance(found.error, ValueError)

    def test_a_symlink_loop_is_unresolvable_and_carries_the_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop.md"
            loop.symlink_to("loop.md")

            found = resolve_within(loop, Boundary.at(root))

        self.assertIs(found.verdict, Verdict.UNRESOLVABLE)
        self.assertIsNotNone(found.error)

    def test_an_unresolvable_boundary_makes_every_candidate_unresolvable(self) -> None:
        # Resolving the root can fail the same way resolving a candidate can, so it
        # is reported the same way instead of escaping as an exception.
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "loop"
            root.symlink_to("loop", target_is_directory=True)

            boundary = Boundary.at(root)
            found = resolve_within(root / "anything.md", boundary)

        self.assertIsNone(boundary.root)
        self.assertIsNotNone(boundary.error)
        self.assertIs(found.verdict, Verdict.UNRESOLVABLE)
        self.assertIs(found.error, boundary.error)

    def test_a_boundary_holds_its_root_already_resolved(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            real = parent / "real"
            real.mkdir()
            alias = parent / "alias"
            alias.symlink_to(real, target_is_directory=True)

            self.assertEqual(Boundary.at(alias).root, real.resolve())


if __name__ == "__main__":
    unittest.main()
