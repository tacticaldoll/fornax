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
            "single quoted": ("'value'", "quoted and flow-style scalars are unsupported"),
            "double quoted": ('"value"', "quoted and flow-style scalars are unsupported"),
            "flow list": ("[one, two]", "quoted and flow-style scalars are unsupported"),
            "flow mapping": ("{one: two}", "quoted and flow-style scalars are unsupported"),
            "literal multiline": ("|", "multiline scalars are unsupported"),
            "folded multiline": (">", "multiline scalars are unsupported"),
            "anchor": ("&shared value", "YAML anchors, aliases, and tags are unsupported"),
            "alias": ("*shared", "YAML anchors, aliases, and tags are unsupported"),
            "tag": ("!custom value", "YAML anchors, aliases, and tags are unsupported"),
        }
        for label, (value, message) in cases.items():
            with self.subTest(label=label), self.assertRaisesRegex(
                FixtureError, re.escape(message)
            ):
                constrained_yaml.raw_scalar(value, 3, FixtureError)
