from __future__ import annotations

import subprocess
import unittest
from os.path import commonpath
from pathlib import Path
from tempfile import TemporaryDirectory

import check_text


def check(*files: Path) -> list[check_text.Diagnostic]:
    root = Path(commonpath([str(path.parent) for path in files]))
    return check_text.check(list(files), root)


class TextHygiene(unittest.TestCase):
    def test_invalid_utf8_markdown_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_bytes(b"# invalid \xff\n")

            errors = check(path)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].path, path)
        self.assertEqual(errors[0].message, "Markdown file must use UTF-8")

    def test_missing_terminal_newline_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("no newline", encoding="utf-8")
            errors = check(path)
        self.assertIn("must end with a newline", errors[0].message)

    def test_missing_local_markdown_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [missing](missing.md).\n", encoding="utf-8")
            errors = check(path)
        self.assertIn("link not found", errors[0].message)

    def test_absolute_markdown_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [absolute](/docs/example.md).\n", encoding="utf-8")
            errors = check(path)

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

            errors = check(source, target, spaced_target)

        self.assertEqual(errors, [])

    def test_link_titles_preserve_missing_and_absolute_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(
                "See [missing](missing.md \"overview\") and "
                "[absolute](/docs/example.md 'overview').\n",
                encoding="utf-8",
            )

            errors = check(path)

        self.assertEqual(len(errors), 2)
        self.assertIn("link not found: missing.md \"overview\"", errors[0].message)
        self.assertIn("absolute Markdown link is not allowed", errors[1].message)

    def test_padded_missing_link_is_checked(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [missing]( missing.md ).\n", encoding="utf-8")

            errors = check(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("link not found: missing.md", errors[0].message)

    def test_percent_encoded_fragment_marker_is_checked_as_a_filename(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            path = parent / "fixture.md"
            path.write_text("See [guide](target%23part.md).\n", encoding="utf-8")
            (parent / "target#part.md").write_text("# Target\n", encoding="utf-8")

            errors = check(path)

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

            errors = check(path)

        self.assertEqual(errors, [])

    def test_code_spans_are_ignored_but_escaped_labels_are_checked(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(
                "`[example](inside-code.md)` and "
                r"[doc \] page](missing.md)" + "\n",
                encoding="utf-8",
            )

            errors = check(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("link not found: missing.md", errors[0].message)

    def test_code_spans_do_not_hide_links_in_later_paragraphs(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(
                "` lone\n\nSee [missing](missing.md).\n\n` later\n",
                encoding="utf-8",
            )

            errors = check(path)

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

                errors = check(path)

            self.assertEqual(len(errors), 1)
            self.assertIn("link not found: missing.md", errors[0].message)

    def test_a_colon_in_the_source_path_remains_structured(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp) / "with:colon"
            parent.mkdir()
            path = parent / "fixture.md"
            path.write_text("no newline", encoding="utf-8")
            errors = check(path)

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
            errors = check(source, target, binary)
        self.assertEqual(errors, [])

    def test_parent_link_that_remains_in_the_repository_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            source = docs / "source.md"
            source.write_text("[target](../target.md)\n", encoding="utf-8")
            (root / "target.md").write_text("# Target\n", encoding="utf-8")

            errors = check_text.check([source], root)

        self.assertEqual(errors, [])

    def test_link_that_leaves_the_repository_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            source = root / "source.md"
            source.write_text("[outside](../outside.md)\n", encoding="utf-8")
            (parent / "outside.md").write_text("# Outside\n", encoding="utf-8")

            errors = check_text.check([source], root)

        self.assertEqual(len(errors), 1)
        self.assertIn("link leaves repository", errors[0].message)

    def test_link_cannot_escape_through_a_symlink(self) -> None:
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            outside = parent / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            (root / "alias.md").symlink_to(outside)
            source = root / "source.md"
            source.write_text("[outside](alias.md)\n", encoding="utf-8")

            errors = check_text.check([source], root)

        self.assertEqual(len(errors), 1)
        self.assertIn("link leaves repository", errors[0].message)

    def test_symlink_loop_fails_without_a_traceback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "loop.md").symlink_to("loop.md")
            source = root / "source.md"
            source.write_text("[loop](loop.md)\n", encoding="utf-8")

            errors = check_text.check([source], root)

        self.assertEqual(len(errors), 1)
        self.assertIn("link could not be resolved", errors[0].message)

    def test_a_windows_absolute_link_is_not_treated_as_external(self) -> None:
        # A drive letter is a valid one-character URI scheme, so this matched as
        # external and skipped the absolute-link rule on every host.
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text("See [guide](C:/docs/guide.md).\n", encoding="utf-8")

            errors = check(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("absolute Markdown link is not allowed", errors[0].message)

    def test_a_tracked_symlink_that_escapes_to_a_missing_target_is_reported(self) -> None:
        # The escape guard used to sit behind is_file(), which is false for a broken
        # symlink, so exactly the malformed cases were skipped in silence.
        with TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            alias = root / "alias.md"
            alias.symlink_to(parent / "never-created.md")

            errors = check_text.check([alias], root)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].message, "tracked path leaves repository")

    def test_a_tracked_symlink_loop_is_reported_not_skipped(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop.md"
            loop.symlink_to("loop.md")

            errors = check_text.check([loop], root)

        self.assertEqual(len(errors), 1)
        self.assertIn("tracked path could not be resolved", errors[0].message)

    def test_a_tracked_path_absent_from_the_working_tree_is_skipped(self) -> None:
        # git ls-files --cached lists index entries whose file was deleted without
        # staging the deletion. Failing on those would break an ordinary commit, so
        # absence is a skip rather than a diagnostic.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            errors = check_text.check([root / "deleted.md"], root)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
