"""Cover the non-Python source parser: it must not report clean without parsing."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import check_sources


class SourceParsingTests(unittest.TestCase):
    def workspace(self, root: Path, body: str) -> None:
        # A worktree, because the check now asks git which files it ships. A root that
        # is not one is a failure the check reports, not a state these cases are in.
        subprocess.run(["git", "init", "-q", str(root)], check=True)
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
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)

            errors = check_sources.check(root)

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

    def test_a_root_that_is_not_a_worktree_is_reported(self) -> None:
        # The listing raises there, and reading that as "no YAML to check" would make
        # this gate answer clean for a release tarball it never looked inside.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "echo ok\n")
            subprocess.run(["rm", "-rf", str(root / ".git")], check=True)

            errors = check_sources.check(root)

            self.assertTrue(any("could not be listed" in error for error in errors), errors)

    def test_this_repository_parses(self) -> None:
        self.assertEqual(check_sources.check(check_sources.ROOT), [])


class YamlParsingTests(unittest.TestCase):
    def workspace(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        hook = root / ".githooks" / "pre-commit"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text("#!/usr/bin/env bash\ntrue\n", encoding="utf-8")

    def track(self, root: Path, name: str, text: str) -> None:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", name], check=True)

    def test_a_tracked_yaml_a_parser_cannot_read_is_reported(self) -> None:
        # A `.yaml` extension is a claim, and this repository's own registries
        # did not meet it: a plain scalar holding ": ", which YAML forbids, read by
        # the hand-written readers written for them and by nothing else. Nothing could
        # see it, because nothing had ever asked a YAML parser to read them.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root)
            self.track(root, "registry.yaml", "note: Gate 5: Responsibility\n")

            errors = check_sources.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("registry.yaml is not YAML", errors[0])

    def test_tracked_yaml_that_parses_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root)
            self.track(root, "registry.yaml", 'note: "Gate 5: Responsibility"\n')

            self.assertEqual(check_sources.check(root), [])

    def test_the_files_are_derived_from_the_workspace_not_listed(self) -> None:
        # A registry added where nobody thought to register it is read like the rest.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root)
            self.track(root, "docs/deep/unregistered.yml", "a: b: c\n")

            errors = check_sources.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("docs/deep/unregistered.yml", errors[0])

    def test_this_repository_s_own_yaml_all_parses(self) -> None:
        self.assertEqual(check_sources.yaml_documents(check_sources.ROOT), ([], None))


if __name__ == "__main__":
    unittest.main()
