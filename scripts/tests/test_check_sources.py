"""Cover the non-Python source parser: it must not report clean without parsing."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import check_sources


class SourceParsingTests(unittest.TestCase):
    def workspace(self, root: Path, body: str) -> None:
        path = root / ".githooks" / "pre-commit"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def test_a_parsing_source_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "#!/usr/bin/env bash\nset -e\necho ok\n")

            self.assertEqual(check_sources.check(root), [])

    def test_a_syntax_error_is_reported_with_what_the_parser_said(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "#!/usr/bin/env bash\nif true; then\n")

            errors = check_sources.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("does not parse", errors[0])

    def test_a_missing_source_fails_rather_than_being_skipped(self) -> None:
        # Reporting clean on an absent file makes this gate say the same thing whether
        # it parsed the hook or never opened it.
        with TemporaryDirectory() as tmp:
            errors = check_sources.check(Path(tmp))

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("is missing", errors[0])

    def test_an_absent_parser_fails_rather_than_being_skipped(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "echo ok\n")
            original = check_sources.PARSERS
            check_sources.PARSERS = ((".githooks/pre-commit", ("definitely-not-a-shell", "-n")),)
            try:
                errors = check_sources.check(root)
            finally:
                check_sources.PARSERS = original

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("not on PATH", errors[0])

    def test_this_repository_parses(self) -> None:
        self.assertEqual(check_sources.check(check_sources.ROOT), [])


if __name__ == "__main__":
    unittest.main()
