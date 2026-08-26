from __future__ import annotations

import re
import unittest

import constrained_yaml


class FixtureError(ValueError):
    pass


class RawScalarTests(unittest.TestCase):
    def test_plain_scalar_round_trips(self) -> None:
        self.assertEqual(
            constrained_yaml.raw_scalar("plain scalar", 3, FixtureError),
            "plain scalar",
        )

    def test_unsupported_scalar_syntax_uses_the_requested_error(self) -> None:
        cases = {
            "empty": ("", "line 3: scalar must not be empty"),
            "single quoted": (
                "'value'",
                "single-quoted and flow-style scalars are unsupported",
            ),
            "flow list": (
                "[one, two]",
                "single-quoted and flow-style scalars are unsupported",
            ),
            "flow mapping": (
                "{one: two}",
                "single-quoted and flow-style scalars are unsupported",
            ),
            "colon space in a plain scalar": (
                "Gate 5: Responsibility",
                "a plain scalar may not hold ': '",
            ),
            "a plain scalar ending in a colon": ("trailing:", "a plain scalar may not hold ': '"),
            "text after the closing quote": ('"one" two', "line 3:"),
            # Quoting had become the way around the comment rule one line above it:
            # YAML ends the scalar at the quote and reads the rest as a comment, so
            # `"value" # note` came back as `value` and the file said something else.
            "comment after the closing quote": ('"one" # note', "comments are unsupported"),
            "comment after a quoted colon value": (
                '"Gate 5: Responsibility"  # note',
                "comments are unsupported",
            ),
            "quote that does not close": ('"one', "line 3:"),
            "literal multiline": ("|", "multiline scalars are unsupported"),
            "folded multiline": (">", "multiline scalars are unsupported"),
            # Every indicator form. Comparing the whole value against the two bare
            # tokens stored these as the value instead of refusing them.
            "literal stripped": ("|-", "multiline scalars are unsupported"),
            "literal kept": ("|+", "multiline scalars are unsupported"),
            "folded stripped": (">-", "multiline scalars are unsupported"),
            "folded kept": (">+", "multiline scalars are unsupported"),
            "literal indented": ("|2", "multiline scalars are unsupported"),
            "literal indented and stripped": ("|2-", "multiline scalars are unsupported"),
            "anchor": ("&shared value", "YAML anchors, aliases, and tags are unsupported"),
            "alias": ("*shared", "YAML anchors, aliases, and tags are unsupported"),
            "tag": ("!custom value", "YAML anchors, aliases, and tags are unsupported"),
            "trailing comment": ("value # note", "comments are unsupported"),
            "comment as the whole value": ("# note", "comments are unsupported"),
        }
        for label, (value, message) in cases.items():
            with self.subTest(label=label), self.assertRaisesRegex(
                FixtureError, re.escape(message)
            ):
                constrained_yaml.raw_scalar(value, 3, FixtureError)

    def test_a_sigil_after_the_first_character_is_ordinary_text(self) -> None:
        # YAML reads &, * and ! as node properties only where a node starts. A rule
        # that also fired mid-value refused prose and shell fragments the registry
        # legitimately contains, and no fixture proved that branch either way.
        for value in ("covers *.py files", "run a && b", "use !important here"):
            with self.subTest(value=value):
                self.assertEqual(constrained_yaml.raw_scalar(value, 3, FixtureError), value)

    def test_a_hash_inside_a_word_is_not_a_comment(self) -> None:
        # YAML only starts a comment at a line start or after whitespace, so this
        # must round-trip rather than be rejected with the comment cases above.
        self.assertEqual(
            constrained_yaml.raw_scalar("issue#42 stays", 3, FixtureError),
            "issue#42 stays",
        )
