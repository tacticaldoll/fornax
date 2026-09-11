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


class ConstructionTests(unittest.TestCase):
    def test_a_prefix_match_cannot_be_made_into_a_whole(self) -> None:
        # The module claimed this was impossible because only whole() built a Whole.
        # That was a convention, and a convention is what the rounds before it had:
        # the dataclass constructor took a prefix match and reported it as a complete
        # read. The invariant is checked where it is stated now.
        with self.assertRaises(ValueError) as raised:
            read_whole.Whole(PIN.match("ruff==0.16.1|x"))

        self.assertIn("not all of it", str(raised.exception))

    def test_a_match_from_the_middle_of_a_subject_is_not_a_whole(self) -> None:
        # search() and finditer() produce these, and either would have reported the
        # token it found as the whole of the text it was given.
        with self.assertRaises(ValueError):
            read_whole.Whole(PIN.search("install ruff==0.16.1 now"))

    def test_a_full_match_is_accepted(self) -> None:
        self.assertEqual(read_whole.Whole(PIN.fullmatch("ruff==0.16.1")).value, "ruff==0.16.1")


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

    def test_a_comment_is_declined_rather_than_located(self) -> None:
        # Where the shell's comment begins has no owner installable here, so the question
        # is declined. A hash inside a word is untouched and a whole-line comment needs no
        # grammar to see; an inline one leaves the command unread.
        self.assertEqual(
            read_whole.shell_words("pip install tool==1.0#x"),
            ["pip", "install", "tool==1.0#x"],
        )
        self.assertEqual(read_whole.shell_words("# pip install t==1.0"), [])

        read = read_whole.shell_words("pip install t==1.0  # note")

        self.assertIsInstance(read, read_whole.Unread)
        self.assertEqual(read.text, "pip install t==1.0  # note")

    def test_text_the_lexer_cannot_finish_is_unread_not_partial(self) -> None:
        read = read_whole.shell_words('echo "unbalanced')

        self.assertIsInstance(read, read_whole.Unread)
        self.assertEqual(read.text, 'echo "unbalanced')

    def test_a_hash_inside_quotes_is_not_a_comment(self) -> None:
        # The cut used to run before the lexer, on a matcher that cannot read a quote, so
        # each of these lost its closing quote and came back unread. bash prints
        # `value # kept` for both.
        for command in ('echo "value # kept"', "echo 'value # kept'"):
            with self.subTest(command=command):
                self.assertEqual(read_whole.shell_words(command), ["echo", "value # kept"])

    def test_an_escaped_hash_is_declined_rather_than_guessed(self) -> None:
        # posix `shlex` unescapes, so `\#` reaches the word list as the token a comment
        # would and nothing at that level tells them apart. bash prints `# literal`, so
        # this is a command the module could once read and now refuses — the cost of
        # declining, stated rather than discovered.
        read = read_whole.shell_words("echo \\# literal")

        self.assertIsInstance(read, read_whole.Unread)

    def test_adjacent_quotes_are_one_word(self) -> None:
        # The control that refuses a cut made by rejoining a scan's tokens: a scan that
        # keeps quotes reads `"x"\'y\'` as two, and rejoining them invents a boundary the
        # shell does not have. bash prints `xy`.
        self.assertEqual(read_whole.shell_words("echo \"x\"'y'"), ["echo", "xy"])

    def test_a_hash_after_a_closing_quote_stays_in_its_word(self) -> None:
        # The scan ends a token at a closing quote, so a hash touching one opens a new
        # token while opening no shell word. Asking only whether a token began was this
        # module's own rule wearing the lexer's name, and it dropped the word and every
        # word after it. bash prints `a#b`, and `a#b keepme` for the second.
        self.assertEqual(read_whole.shell_words('echo "a"#b'), ["echo", "a#b"])
        self.assertEqual(read_whole.shell_words("echo 'a'#b"), ["echo", "a#b"])
        self.assertEqual(
            read_whole.shell_words('echo "a"#b keepme'), ["echo", "a#b", "keepme"]
        )

    def test_a_hash_after_an_escaped_separator_keeps_its_word(self) -> None:
        # The escape joins the space into the word, so no word opens with a hash and the
        # command reads. bash prints `a #b`. Declining the question gets this right where
        # three rounds of locating it did not.
        self.assertEqual(read_whole.shell_words("echo a\\ #b"), ["echo", "a #b"])

    def test_text_after_a_hash_is_lexed_and_can_leave_the_command_unread(self) -> None:
        # The whole command is lexed now, so an unfinishable quote after a hash is reached
        # rather than cut away. bash prints `a`; this refuses. The other half of the same
        # trade as the escaped hash above.
        read = read_whole.shell_words('echo a # "unbalanced')

        self.assertIsInstance(read, read_whole.Unread)


class CommentRule(unittest.TestCase):
    """A hash that could open a word leaves the command unread, wherever it sits.

    The rule used to be located: a hash beginning a word, for three successive readings
    of "beginning a word". Each closed the case a review named and reopened the class
    beside it, because the shell's comment rule has no owner this repository may install
    and every reading of it was therefore hand-written.

    So these cases assert a refusal rather than a cut. What is not refused is a hash that
    cannot be a comment: one inside a word, and one opening the command, where nothing
    precedes it that could quote it.
    """

    def test_a_hash_that_could_open_a_word_leaves_the_command_unread(self) -> None:
        for command in (
            "pip install a==1;# pip install evil==9",
            "true&&# pip install evil==9",
            "true|# pip install evil==9",
            "(pip install a==1)#x",
            "pip install a==1 # x",
        ):
            with self.subTest(command=command):
                read = read_whole.shell_words(command)

                self.assertIsInstance(read, read_whole.Unread)
                self.assertEqual(read.text, command)

    def test_a_hash_inside_a_word_is_not_a_comment(self) -> None:
        # The near-miss control: the same character, not opening a word. bash prints both
        # of these whole, and a pin or a URL fragment must survive.
        self.assertEqual(
            read_whole.shell_words("pip install a==1#notacomment"),
            ["pip", "install", "a==1#notacomment"],
        )
        self.assertEqual(
            read_whole.shell_words("pip install git+https://h/p#egg=z"),
            ["pip", "install", "git+https://h/p#egg=z"],
        )

    def test_a_command_opening_with_a_hash_is_a_comment_whole(self) -> None:
        # The accepted-side spelling: a hash at the first non-blank character needs no
        # grammar, nothing before it being able to quote it.
        self.assertEqual(read_whole.shell_words("# pip install evil==9"), [])
        self.assertEqual(read_whole.shell_words("   # indented and whole"), [])


class RequirementsComment(unittest.TestCase):
    """`read_whole.COMMENT` reads a requirements line, and nothing else reaches it.

    It was shared with `shell_words`, whose tests were its only coverage. When that call
    went the coverage went with it, and because no symbol was renamed nothing reported
    it: a `docs/guards.md` row kept instructing a later round to revert a rule that
    reverting no longer reddened. This class reaches the pattern for its own sake, so
    severing a caller cannot silence it again.
    """

    def test_a_hash_at_the_start_or_after_whitespace_begins_a_comment(self) -> None:
        self.assertEqual(
            read_whole.COMMENT.split("ruff==1.0 # pin", maxsplit=1)[0], "ruff==1.0 "
        )
        self.assertEqual(read_whole.COMMENT.split("# all of it", maxsplit=1)[0], "")

    def test_a_hash_inside_a_word_is_not_a_comment(self) -> None:
        # The near-miss control, sharing the accepted character: pip's URL fragment and a
        # pin carrying a hash both have to survive whole.
        for line in ("pkg#egg=z", "ruff==1.0#x"):
            with self.subTest(line=line):
                self.assertEqual(read_whole.COMMENT.split(line, maxsplit=1)[0], line)

    def test_a_hash_after_a_marker_separator_is_not_a_comment(self) -> None:
        # The alternate spelling of the same meaning: a hash beginning a word where the
        # shell would have said so, written with an operator rather than a space. Retired
        # with the shell, so the line is left whole and reaches `packaging`, which refuses
        # it rather than comparing a truncation clean.
        self.assertEqual(
            read_whole.COMMENT.split("ruff==1.0;#x", maxsplit=1)[0], "ruff==1.0;#x"
        )


if __name__ == "__main__":
    unittest.main()
