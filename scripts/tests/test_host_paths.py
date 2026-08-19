from __future__ import annotations

import unittest

from host_paths import has_parent_segment_anywhere, is_absolute_anywhere


class HostPathTests(unittest.TestCase):
    def test_either_grammar_makes_a_path_absolute(self) -> None:
        for value in ("/abs.md", "C:/docs/guide.md", "C:x", r"\\server\share\x"):
            with self.subTest(value=value):
                self.assertTrue(is_absolute_anywhere(value))

    def test_a_relative_path_stays_relative(self) -> None:
        for value in ("docs/a.md", "x/y.md", "../shared", r"..\shared"):
            with self.subTest(value=value):
                self.assertFalse(is_absolute_anywhere(value))

    def test_a_real_uri_scheme_is_not_a_drive(self) -> None:
        # Only one letter can be a drive, so these must stay out of the way of the
        # scheme test in markdown_links.
        for value in ("https://example.com/x", "mailto:a@b.c", "agentskills.io"):
            with self.subTest(value=value):
                self.assertFalse(is_absolute_anywhere(value))

    def test_a_backslash_traversal_is_seen_even_where_it_is_a_filename(self) -> None:
        # PurePosixPath reads "..\\shared" as one filename; PureWindowsPath reads a
        # traversal. This is the case the running host's grammar alone would miss.
        self.assertTrue(has_parent_segment_anywhere(r"..\shared"))
        self.assertTrue(has_parent_segment_anywhere("../shared"))
        self.assertTrue(has_parent_segment_anywhere("a/../b"))

    def test_an_ordinary_path_has_no_parent_segment(self) -> None:
        for value in ("docs/a.md", "scripts", "a..b/c"):
            with self.subTest(value=value):
                self.assertFalse(has_parent_segment_anywhere(value))


if __name__ == "__main__":
    unittest.main()
