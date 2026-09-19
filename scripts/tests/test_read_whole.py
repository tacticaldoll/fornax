from __future__ import annotations

import re
import unittest

from agent_skill_format import read_whole

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


class RequirementsComment(unittest.TestCase):
    """`read_whole.COMMENT` reads a requirements line, and nothing else reaches it.

    It was shared with `shell_words`, whose tests were its only coverage. When that call
    went the coverage went with it, and because no symbol was renamed nothing reported
    it: a dated guard entry kept instructing a later round to revert a rule that
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
        # A second near-miss, not an alternate spelling — this asserts the line is *not*
        # cut, exactly as the case above does. It was labelled the other way, which left
        # the accepted side of the rule with no control at all; the case below is that
        # control. Retired with the shell, so the line reaches `packaging`, which refuses
        # it rather than letting a truncation compare clean.
        self.assertEqual(
            read_whole.COMMENT.split("ruff==1.0;#x", maxsplit=1)[0], "ruff==1.0;#x"
        )

    def test_a_hash_after_a_tab_begins_a_comment(self) -> None:
        # The alternate spelling on the accepted side: the rule is whitespace, not a
        # space, and `\s` admits a tab. Nothing exercised it, so the accepted half of
        # the pattern rested on one character.
        self.assertEqual(
            read_whole.COMMENT.split("ruff==1.0\t# pin", maxsplit=1)[0], "ruff==1.0\t"
        )


if __name__ == "__main__":
    unittest.main()
