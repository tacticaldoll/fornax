"""Cover the shared workspace lister and the one place its raise becomes a diagnostic."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import workspace_files


class ListerTests(unittest.TestCase):
    def test_a_worktree_lists_cached_and_untracked_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "tracked.md").write_text("tracked\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.md"], check=True)
            (root / "untracked.md").write_text("untracked\n", encoding="utf-8")

            found, error = workspace_files.listed(root)

            self.assertIsNone(error)
            self.assertEqual({p.name for p in found}, {"tracked.md", "untracked.md"})

    def test_the_raw_lister_raises_rather_than_reporting_an_empty_workspace(self) -> None:
        # The default that must stay: an unlistable workspace is not an empty one.
        with TemporaryDirectory() as tmp:
            with self.assertRaises(subprocess.CalledProcessError):
                workspace_files.workspace_files(Path(tmp))

    def test_a_non_worktree_becomes_a_diagnostic_rather_than_a_traceback(self) -> None:
        # A release tarball or a `git archive` export is a directory a check can be
        # pointed at legitimately, and its callers must report rather than crash.
        with TemporaryDirectory() as tmp:
            found, error = workspace_files.listed(Path(tmp))

            self.assertIsNone(found)
            self.assertIn("workspace could not be listed", error)


if __name__ == "__main__":
    unittest.main()
