from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import runtime_contract


PINNED = {"markdown-it-py": "4.2.0"}


def satisfied(name: str) -> str | None:
    return PINNED.get(name)


class RuntimeContractTests(unittest.TestCase):
    def write_contract(self, root: Path, python_version: str, ruff_version: str) -> None:
        (root / ".python-version").write_text(python_version + "\n", encoding="utf-8")
        (root / "ruff.toml").write_text(
            f'target-version = "{ruff_version}"\n', encoding="utf-8"
        )
        (root / "requirements-maintenance.txt").write_text(
            "markdown-it-py==4.2.0\n", encoding="utf-8"
        )

    def check(self, root: Path, **kwargs) -> list[str]:
        kwargs.setdefault("installed", satisfied)
        return runtime_contract.check(root, **kwargs)

    def test_matching_runtime_and_ruff_target_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root)

        self.assertEqual(errors, [])

    def test_mismatched_ruff_target_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py38")

            errors = self.check(root)

        self.assertEqual(
            errors,
            ["ruff.toml target-version must be py310 to match .python-version"],
        )

    def test_an_interpreter_below_the_declared_floor_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root, running=(3, 8))

        self.assertEqual(len(errors), 1)
        self.assertIn("requires Python 3.10 or newer", errors[0])
        self.assertIn("this interpreter is 3.8", errors[0])
        self.assertIn("README.md", errors[0])

    def test_an_interpreter_at_or_above_the_floor_passes(self) -> None:
        for running in ((3, 10), (3, 12), (4, 0)):
            with self.subTest(running=running), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_contract(root, "3.10", "py310")

                self.assertEqual(self.check(root, running=running), [])

    def test_invalid_or_missing_declarations_fail_cleanly(self) -> None:
        cases = (
            ("3.10.1", 'target-version = "py310"\n', ".python-version must contain major.minor"),
            ("3.10", "line-length = 100\n", "ruff.toml must declare one target-version"),
        )
        for python_version, ruff_text, message in cases:
            with self.subTest(message=message), TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / ".python-version").write_text(
                    python_version + "\n", encoding="utf-8"
                )
                (root / "ruff.toml").write_text(ruff_text, encoding="utf-8")

                errors = self.check(root)

            self.assertIn(message, errors)


    def test_a_pinned_library_at_another_version_fails(self) -> None:
        # An environment holding a different version satisfies the floor and then
        # validates the workspace with a parser the pins do not name.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root, installed=lambda name: "3.0.0")

        self.assertEqual(len(errors), 1)
        self.assertIn("pinned at 4.2.0 but 3.0.0 is installed", errors[0])
        self.assertIn("README.md", errors[0])

    def test_a_pinned_library_that_is_absent_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root, installed=lambda name: None)

        self.assertEqual(len(errors), 1)
        self.assertIn("is not installed", errors[0])

    def test_a_requirements_file_pinning_nothing_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")
            (root / "requirements-maintenance.txt").write_text(
                "# only a comment\n", encoding="utf-8"
            )

            errors = self.check(root)

        self.assertEqual(
            errors, ["requirements-maintenance.txt must pin at least one name==version"]
        )

    def test_pins_reads_past_a_comment_a_marker_and_pyproject_quoting(self) -> None:
        for line in (
            "markdown-it-py==4.2.0",
            "markdown-it-py==4.2.0  # pinned for CommonMark",
            'markdown-it-py==4.2.0 ; python_version >= "3.10"',
            '  "markdown-it-py==4.2.0",',
        ):
            with self.subTest(line=line):
                self.assertEqual(runtime_contract.pins(line), {"markdown-it-py": "4.2.0"})


class SharedPinTests(unittest.TestCase):
    """The CLI declares the libraries the workspace validator imports, because
    snapshot validation shells out to it. Where both files name a package they must
    name the same version, or one pinned tag validates differently between runs.

    This lives here rather than beside the CLI because it reads two files and needs
    nothing the deployment engine provides — and beside the CLI it ran only after
    that engine installed, so the invariant went unchecked whenever it did not.
    """

    def test_shared_dependencies_name_the_same_version(self) -> None:
        root = Path(__file__).resolve().parents[2]
        maintenance = runtime_contract.pins(
            (root / "requirements-maintenance.txt").read_text(encoding="utf-8")
        )
        cli = runtime_contract.pins(
            (root / "tools/fornax-cli/pyproject.toml").read_text(encoding="utf-8")
        )
        shared = maintenance.keys() & cli.keys()

        self.assertTrue(shared, "no dependency is shared, so this asserts nothing")
        for name in sorted(shared):
            with self.subTest(name=name):
                self.assertEqual(cli[name], maintenance[name])


if __name__ == "__main__":
    unittest.main()
