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
            step.argv[0] for step in check_workspace.STEPS if step.argv[0].endswith(".py")
        ]

        self.assertTrue(scripts)
        for script in scripts:
            with self.subTest(script=script):
                self.assertTrue((check_workspace.ROOT / script).is_file())

    def test_every_step_describes_itself_for_the_generated_list(self) -> None:
        # README's list of these was transcribed and went stale. It is derived now, so a
        # step with no description would generate a blank line rather than fail — which
        # is how the drift stayed invisible the first time.
        for step in check_workspace.STEPS:
            with self.subTest(step=step.label):
                self.assertTrue(step.description.strip(), step.label)

    def test_every_generated_block_is_checked_by_the_gate(self) -> None:
        # A generator with tests but no wiring passes every one of them while its
        # committed block goes stale unwatched — which is what a whole test file for
        # gate_steps proved, and did not prove, when the step was left out of STEPS.
        scripts = sorted(
            path.name
            for path in (check_workspace.ROOT / "scripts").glob("*.py")
            if "generated_block.dispatch" in path.read_text(encoding="utf-8")
        )
        checked = {
            step.argv[0]
            for step in check_workspace.STEPS
            if len(step.argv) > 1 and step.argv[1] == "--check"
        }

        self.assertTrue(scripts)
        for name in scripts:
            with self.subTest(script=name):
                self.assertIn(f"scripts/{name}", checked)

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
