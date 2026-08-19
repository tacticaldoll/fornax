from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import runtime_contract


class RuntimeContractTests(unittest.TestCase):
    def write_contract(self, root: Path, python_version: str, ruff_version: str) -> None:
        (root / ".python-version").write_text(python_version + "\n", encoding="utf-8")
        (root / "ruff.toml").write_text(
            f'target-version = "{ruff_version}"\n', encoding="utf-8"
        )

    def test_matching_runtime_and_ruff_target_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = runtime_contract.check(root)

        self.assertEqual(errors, [])

    def test_mismatched_ruff_target_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py38")

            errors = runtime_contract.check(root)

        self.assertEqual(
            errors,
            ["ruff.toml target-version must be py310 to match .python-version"],
        )

    def test_an_interpreter_below_the_declared_floor_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = runtime_contract.check(root, running=(3, 8))

        self.assertEqual(len(errors), 1)
        self.assertIn("requires Python 3.10 or newer", errors[0])
        self.assertIn("this interpreter is 3.8", errors[0])
        self.assertIn("README.md", errors[0])

    def test_an_interpreter_at_or_above_the_floor_passes(self) -> None:
        for running in ((3, 10), (3, 12), (4, 0)):
            with self.subTest(running=running), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_contract(root, "3.10", "py310")

                self.assertEqual(runtime_contract.check(root, running=running), [])

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

                errors = runtime_contract.check(root)

            self.assertIn(message, errors)


if __name__ == "__main__":
    unittest.main()
