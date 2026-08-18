from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import check_text


class TextHygiene(unittest.TestCase):
    def test_missing_terminal_newline_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("no newline", encoding="utf-8")
            errors = check_text.check([path])
        self.assertIn("must end with a newline", errors[0])

    def test_missing_local_markdown_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [missing](missing.md).\n", encoding="utf-8")
            errors = check_text.check([path])
        self.assertIn("link not found", errors[0])

    def test_valid_text_and_binary_files_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.md"
            target.write_text("target\n", encoding="utf-8")
            source = root / "source.md"
            source.write_text("See [target](target.md).\n", encoding="utf-8")
            binary = root / "image.bin"
            binary.write_bytes(b"not text\0without newline")
            errors = check_text.check([source, target, binary])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
