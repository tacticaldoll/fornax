from __future__ import annotations

import unittest

from diagnostic_text import printable

ESC = chr(0x1B)
CR = chr(0x0D)
RLO = chr(0x202E)


class DiagnosticTextTests(unittest.TestCase):
    def test_an_escape_sequence_cannot_rewrite_the_line(self) -> None:
        shown = printable(f"FAIL thing - {ESC}[2Kquiet{CR}OK   all good")

        self.assertNotIn(ESC, shown)
        self.assertNotIn(CR, shown)
        self.assertIn("\\x1b[2Kquiet\\x0dOK   all good", shown)

    def test_an_override_cannot_reverse_the_line(self) -> None:
        # Trojan Source, pointed at a validator's own report: this renders as
        # "SKILL.md not SKILL.md" unless the override is shown.
        shown = printable(f"entrypoint not found: SKILL.md{RLO}dm.LLIKS ton")

        self.assertNotIn(RLO, shown)
        self.assertIn("SKILL.md\\u202edm.LLIKS ton", shown)

    def test_every_hiding_category_is_shown(self) -> None:
        for code, expected in (
            (0x00, "\\x00"),      # Cc
            (0x1B, "\\x1b"),      # Cc
            (0x9B, "\\x9b"),      # Cc, C1
            (0x200B, "\\u200b"),  # Cf, zero width
            (0x202E, "\\u202e"),  # Cf, bidi override
            (0x2028, "\\u2028"),  # Zl
            (0x2029, "\\u2029"),  # Zp
            (0xE0001, "\\U000e0001"),  # Cf above the BMP
        ):
            with self.subTest(code=code):
                self.assertEqual(printable(chr(code)), expected)

    def test_visible_text_of_any_script_is_untouched(self) -> None:
        for text in (
            "FAIL example-skill - entrypoint not found: SKILL.md",
            "docs/identity.md — the brand rationale",
            "触发词与本地化示例",
            "a private-use glyph  renders as a font chooses",
            f"a lone emoji {chr(0x1F600)} is visible",
        ):
            with self.subTest(text=text):
                self.assertEqual(printable(text), text)

    def test_a_joined_emoji_sequence_is_shown_and_that_is_the_trade(self) -> None:
        # U+200D is Cf. Pinning the cost as a decision rather than leaving it to be
        # discovered: an exception for it would restore the hand-maintained list.
        joined = f"{chr(0x1F468)}{chr(0x200D)}{chr(0x1F469)}"

        self.assertEqual(printable(joined), f"{chr(0x1F468)}\\u200d{chr(0x1F469)}")


if __name__ == "__main__":
    unittest.main()
