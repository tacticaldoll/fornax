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
