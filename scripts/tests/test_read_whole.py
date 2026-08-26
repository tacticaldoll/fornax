from __future__ import annotations

import re
import unittest

import read_whole

PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][0-9A-Za-z.!+*_-]*)")


class WholeTests(unittest.TestCase):
    def test_a_token_the_pattern_covers_entirely_is_read(self) -> None:
        read = read_whole.whole("ruff==0.16.1", PIN, "an exact pin")

        self.assertIsInstance(read, read_whole.Whole)
        self.assertEqual(read.value, "ruff==0.16.1")
        self.assertEqual((read.group(1), read.group(2)), ("ruff", "0.16.1"))

    def test_a_token_the_pattern_covers_partly_is_unread_not_shortened(self) -> None:
        # The whole point. Every one of these has a prefix the pattern matches, and
        # under a prefix match each became a well-formed value that compared equal to
        # something and answered clean.
        for text in ("ruff==0.16.1|x", "ruff==0.16.1#x", "ruff==0.16.1 and more"):
            with self.subTest(text=text):
                read = read_whole.whole(text, PIN, "an exact pin")

                self.assertIsInstance(read, read_whole.Unread)
                self.assertEqual(read.text, text)

    def test_an_unread_carries_the_text_it_could_not_finish(self) -> None:
        # A caller holding this has nothing nearly-right to compare, which is what
        # makes reporting the only thing left to do with it.
        read = read_whole.whole("ruff==x.y.z", PIN, "an exact pin")

        self.assertIn("ruff==x.y.z", str(read))
        self.assertIn("is not an exact pin", str(read))
        self.assertFalse(hasattr(read, "value"))


class ShellWordTests(unittest.TestCase):
    def test_quoting_bounds_a_word_and_operators_end_one(self) -> None:
        for command, expected in (
            ("pip install tool==1.2.3", ["pip", "install", "tool==1.2.3"]),
            (
                "pip install ruff==0.16.1|tee out",
                ["pip", "install", "ruff==0.16.1", "|", "tee", "out"],
            ),
            (
                "pip install ruff==0.16.1; echo done",
                ["pip", "install", "ruff==0.16.1", ";", "echo", "done"],
            ),
            (
                'pip install "a @ git+https://h/r.git@v1#subdirectory=t"',
                ["pip", "install", "a @ git+https://h/r.git@v1#subdirectory=t"],
            ),
        ):
            with self.subTest(command=command):
                self.assertEqual(read_whole.shell_words(command), expected)

    def test_a_comment_is_cut_where_the_shell_cuts_one(self) -> None:
        # shlex ends a word at any `#`, so it reads `tool==1.0#x` as `tool==1.0` — the
        # truncation this module exists to stop, arriving from the library. Checked
        # against the shell itself: `bash -c 'echo tool==1.0#x'` prints `tool==1.0#x`.
        kept = read_whole.shell_words("pip install tool==1.0#x")
        self.assertEqual(kept, ["pip", "install", "tool==1.0#x"])
        cut = read_whole.shell_words("pip install t==1.0  # note")
        self.assertEqual(cut, ["pip", "install", "t==1.0"])
        self.assertEqual(read_whole.shell_words("# pip install t==1.0"), [])

    def test_text_the_lexer_cannot_finish_is_unread_not_partial(self) -> None:
        read = read_whole.shell_words('echo "unbalanced')

        self.assertIsInstance(read, read_whole.Unread)
        self.assertEqual(read.text, 'echo "unbalanced')


if __name__ == "__main__":
    unittest.main()
