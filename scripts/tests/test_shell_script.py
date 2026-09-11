"""Hold the three rules, and the decline that makes the third exact."""

from __future__ import annotations

import unittest

import read_whole
import shell_script


class OneLine(unittest.TestCase):
    """A script of one line carries no boundary question."""

    def test_one_line_is_one_command(self) -> None:
        found = shell_script.commands("pip install ruff==1.0")

        self.assertEqual([c.text for c in found], ["pip install ruff==1.0"])

    def test_a_quote_on_one_line_is_not_declined(self) -> None:
        # Every run value this repository actually carries is one line, and one of them
        # holds a quote. Declining it would cost the only input there is.
        found = shell_script.commands('pip install "a @ git+https://h/r.git@v1"')

        self.assertEqual([c.text for c in found], ['pip install "a @ git+https://h/r.git@v1"'])

    def test_a_blank_or_comment_line_runs_nothing(self) -> None:
        for script in ("", "   ", "# a comment", "   # indented"):
            with self.subTest(script=script):
                self.assertEqual(shell_script.commands(script), [])


class CommentDoesNotContinue(unittest.TestCase):
    """A comment ends at the newline whatever the last character is.

    The defect this module exists for. `runtime_contract` joined the comment onto the
    line below, `read_whole.shell_words` saw a leading hash and answered with no words,
    and the install on the second line was reported by nothing.
    """

    def test_a_comment_ending_in_a_backslash_does_not_swallow_the_next_command(self) -> None:
        found = shell_script.commands("# install it \\\npip install ruff==9.9.9")

        self.assertEqual([c.text for c in found], ["pip install ruff==9.9.9"])

    def test_a_comment_between_commands_is_dropped_and_both_survive(self) -> None:
        found = shell_script.commands("pip install a==1\n# note\npip install b==2")

        self.assertEqual([c.text for c in found], ["pip install a==1", "pip install b==2"])


class Continuation(unittest.TestCase):
    """A line ending in an odd run of backslashes continues; an even run does not."""

    def test_an_odd_run_continues(self) -> None:
        self.assertEqual(
            [c.text for c in shell_script.commands("pip install \\\nruff==1.0")],
            ["pip install ruff==1.0"],
        )

    def test_an_even_run_ends_the_command(self) -> None:
        # The near-miss control, sharing the accepted character. bash reads the pair as
        # one escaped backslash and runs the next line as its own command; joining them
        # loses that command entirely, which is an under-read.
        found = shell_script.commands("echo a\\\\\npip install ruff==9.9.9")

        self.assertEqual([c.text for c in found], ["echo a\\\\", "pip install ruff==9.9.9"])


class Declined(unittest.TestCase):
    """What needs the parser this repository may not install is refused, not guessed."""

    def test_a_multi_line_script_holding_a_quote_is_declined(self) -> None:
        read = shell_script.commands('echo "a\nb"')

        self.assertIsInstance(read, read_whole.Unread)
        self.assertIn("quote", read.reason)

    def test_a_heredoc_is_declined(self) -> None:
        read = shell_script.commands("cat <<EOF\npip install evil==9\nEOF")

        self.assertIsInstance(read, read_whole.Unread)
        self.assertIn("heredoc", read.reason)


class CommandHoldsNoNewline(unittest.TestCase):
    """The invariant a reader of a `Command` is allowed to rely on."""

    def test_a_command_carrying_a_newline_cannot_be_built(self) -> None:
        with self.assertRaises(ValueError):
            shell_script.Command("echo a\necho b")

    def test_every_command_this_returns_holds_none(self) -> None:
        found = shell_script.commands("pip install a==1\npip install b==2 \\\nc==3")

        self.assertTrue(all("\n" not in c.text for c in found), found)


if __name__ == "__main__":
    unittest.main()
