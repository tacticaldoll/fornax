from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

import check_workspace


class WorkspaceChecks(unittest.TestCase):
    @patch("check_workspace.subprocess.run")
    def test_all_steps_are_dispatched_and_success_is_reported(self, run: Mock) -> None:
        run.return_value.returncode = 0

        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            code = check_workspace.main()

        self.assertEqual(code, 0)
        self.assertEqual(run.call_count, len(check_workspace.STEPS))

    def test_every_script_step_names_an_existing_file(self) -> None:
        scripts = [
            arguments[0]
            for _, *arguments in check_workspace.STEPS
            if arguments[0].endswith(".py")
        ]

        self.assertTrue(scripts)
        for script in scripts:
            with self.subTest(script=script):
                self.assertTrue((check_workspace.ROOT / script).is_file())

    @patch("check_workspace.subprocess.run")
    def test_any_failed_step_fails_the_workspace(self, run: Mock) -> None:
        run.side_effect = [
            *[Mock(returncode=0) for _ in range(len(check_workspace.STEPS) - 1)],
            Mock(returncode=1),
        ]

        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            code = check_workspace.main()

        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, len(check_workspace.STEPS))


if __name__ == "__main__":
    unittest.main()
