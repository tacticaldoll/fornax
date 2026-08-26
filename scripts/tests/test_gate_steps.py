from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import check_workspace
import gate_steps

BEFORE = "# Fixture\n\nProse above the block.\n\n"
AFTER = "\nProse below the block.\n"


def run(root: Path, *argv: str) -> tuple[int, str]:
    out = StringIO()
    with patch.object(gate_steps, "ROOT", root), redirect_stdout(out):
        code = gate_steps.main(list(argv))
    return code, out.getvalue()


def write_readme(root: Path, body: str) -> Path:
    path = root / "README.md"
    path.write_text(BEFORE + body + AFTER, encoding="utf-8")
    return path


class GateStepsTests(unittest.TestCase):
    def markers(self) -> str:
        return f"{gate_steps.MARKERS.start}\n{gate_steps.MARKERS.end}\n"

    def test_the_written_list_names_every_step_the_gate_runs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_readme(root, self.markers())

            self.assertEqual(run(root, "--write")[0], 0)

            written = path.read_text(encoding="utf-8")
            for number, step in enumerate(check_workspace.STEPS, 1):
                with self.subTest(step=step.label):
                    self.assertIn(f"{number}. {step.description}", written)

    def test_a_step_added_to_the_gate_makes_the_committed_list_stale(self) -> None:
        # The guarantee the transcribed list did not have. README said eight checks
        # while eleven ran, and nothing could see it, because a count in prose is not
        # a claim any check reads.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_readme(root, self.markers())
            self.assertEqual(run(root, "--write")[0], 0)

            added = (*check_workspace.STEPS, check_workspace.Step("new", "a new check", ("x.py",)))
            with patch.object(check_workspace, "STEPS", added):
                with patch.object(gate_steps, "STEPS", added):
                    code, out = run(root, "--check")

            self.assertEqual(code, 1)
            self.assertIn("out of date", out)

    def test_a_current_list_passes_the_check(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_readme(root, self.markers())
            self.assertEqual(run(root, "--write")[0], 0)

            code, out = run(root, "--check")

            self.assertEqual(code, 0)
            self.assertIn(f"{len(check_workspace.STEPS)} step(s)", out)

    def test_a_readme_without_the_markers_is_reported(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_readme(root, "no markers here\n")

            code, out = run(root, "--check")

            self.assertEqual(code, 1)
            self.assertIn("README.md", out)


if __name__ == "__main__":
    unittest.main()
