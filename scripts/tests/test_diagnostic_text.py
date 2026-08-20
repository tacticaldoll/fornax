from __future__ import annotations

import unittest

from diagnostic_text import printable

ESC = chr(27)
CR = chr(13)


class DiagnosticTextTests(unittest.TestCase):
    def test_a_carriage_return_cannot_rewrite_the_line(self) -> None:
        forged = f"FAIL thing - {ESC}[2Kquiet{CR}OK   all good"

        shown = printable(forged)

        self.assertNotIn(ESC, shown)
        self.assertNotIn(CR, shown)
        self.assertIn("\\x1b[2Kquiet\\x0dOK   all good", shown)

    def test_every_control_codepoint_is_shown(self) -> None:
        for code in (0x00, 0x09, 0x0A, 0x1B, 0x7F, 0x9F):
            with self.subTest(code=code):
                self.assertEqual(printable(chr(code)), f"\\x{code:02x}")

    def test_ordinary_and_non_ascii_text_is_untouched(self) -> None:
        # The diagnostics themselves use an em dash, and skills may carry any script.
        for text in ("FAIL example-skill - entrypoint not found: SKILL.md",
                     "docs/identity.md — the brand rationale",
                     "触发词与本地化示例"):
            with self.subTest(text=text):
                self.assertEqual(printable(text), text)


if __name__ == "__main__":
    unittest.main()
