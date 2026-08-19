from __future__ import annotations

import subprocess
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
        self.assertIn("must end with a newline", errors[0].message)

    def test_missing_local_markdown_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [missing](missing.md).\n", encoding="utf-8")
            errors = check_text.check([path])
        self.assertIn("link not found", errors[0].message)

    def test_absolute_markdown_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [absolute](/docs/example.md).\n", encoding="utf-8")
            errors = check_text.check([path])

        self.assertEqual(errors[0].path, path)
        self.assertIn("absolute Markdown link is not allowed", errors[0].message)

    def test_valid_local_links_with_titles_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.md"
            target.write_text("target\n", encoding="utf-8")
            spaced_target = root / "target file.md"
            spaced_target.write_text("target\n", encoding="utf-8")
            source = root / "source.md"
            source.write_text(
                "See [double](target.md \"overview\"), "
                "[single](target.md 'overview'), and "
                "[angle](<target file.md> \"overview\"), plus "
                "[nested](target.md \"short (local) guide\").\n",
                encoding="utf-8",
            )

            errors = check_text.check([source, target, spaced_target])

        self.assertEqual(errors, [])

    def test_link_titles_preserve_missing_and_absolute_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(
                "See [missing](missing.md \"overview\") and "
                "[absolute](/docs/example.md 'overview').\n",
                encoding="utf-8",
            )

            errors = check_text.check([path])

        self.assertEqual(len(errors), 2)
        self.assertIn("link not found: missing.md \"overview\"", errors[0].message)
        self.assertIn("absolute Markdown link is not allowed", errors[1].message)

    def test_padded_missing_link_is_checked(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [missing]( missing.md ).\n", encoding="utf-8")

            errors = check_text.check([path])

        self.assertEqual(len(errors), 1)
        self.assertIn("link not found: missing.md", errors[0].message)

    def test_percent_encoded_fragment_marker_is_checked_as_a_filename(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            path = parent / "fixture.md"
            path.write_text("See [guide](target%23part.md).\n", encoding="utf-8")
            (parent / "target#part.md").write_text("# Target\n", encoding="utf-8")

            errors = check_text.check([path])

        self.assertEqual(errors, [])

    def test_uri_query_is_not_a_filename_and_network_links_are_external(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            path = parent / "fixture.md"
            path.write_text(
                "[local](target.md?raw=1#section) and "
                "[network](//example.com/guide).\n",
                encoding="utf-8",
            )
            (parent / "target.md").write_text("# Target\n", encoding="utf-8")

            errors = check_text.check([path])

        self.assertEqual(errors, [])

    def test_code_spans_are_ignored_but_escaped_labels_are_checked(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(
                "`[example](inside-code.md)` and "
                r"[doc \] page](missing.md)" + "\n",
                encoding="utf-8",
            )

            errors = check_text.check([path])

        self.assertEqual(len(errors), 1)
        self.assertIn("link not found: missing.md", errors[0].message)

    def test_code_spans_do_not_hide_links_in_later_paragraphs(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(
                "` lone\n\nSee [missing](missing.md).\n\n` later\n",
                encoding="utf-8",
            )

            errors = check_text.check([path])

        self.assertEqual(len(errors), 1)
        self.assertIn("link not found: missing.md", errors[0].message)

    def test_code_spans_do_not_hide_links_across_other_block_boundaries(self) -> None:
        cases = (
            "# ` heading\nSee [missing](missing.md).\n` later\n",
            "- ` first\n- See [missing](missing.md).\n- ` third\n",
        )
        for text in cases:
            with self.subTest(text=text), TemporaryDirectory() as tmp:
                path = Path(tmp) / "fixture.md"
                path.write_text(text, encoding="utf-8")

                errors = check_text.check([path])

            self.assertEqual(len(errors), 1)
            self.assertIn("link not found: missing.md", errors[0].message)

    def test_a_colon_in_the_source_path_remains_structured(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp) / "with:colon"
            parent.mkdir()
            path = parent / "fixture.md"
            path.write_text("no newline", encoding="utf-8")
            errors = check_text.check([path])

        self.assertEqual(errors[0].path, path)
        self.assertEqual(errors[0].message, "text file must end with a newline")

    def test_workspace_files_include_cached_and_untracked_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            tracked = root / "tracked.md"
            tracked.write_text("tracked\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", tracked.name], check=True)
            untracked = root / "untracked.md"
            untracked.write_text("untracked\n", encoding="utf-8")

            files = check_text.workspace_files(root)

        self.assertEqual(set(files), {tracked, untracked})

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
