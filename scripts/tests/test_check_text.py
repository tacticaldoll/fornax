from __future__ import annotations

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

    def test_a_link_holding_an_encoded_null_is_reported_not_raised(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "document.md"
            document.write_text("See [x](a%00b.md).\n", encoding="utf-8")

            errors = check(document)

        self.assertEqual(len(errors), 1)
        self.assertIn("could not be resolved", errors[0].message)

    def test_a_non_markdown_file_is_checked_for_a_newline_but_not_for_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "notes.txt"
            document.write_text("See [missing](gone.md).\n", encoding="utf-8")

            self.assertEqual(check(document), [])

    def test_an_empty_file_is_not_missing_a_newline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            empty = root / "empty.md"
            empty.write_bytes(b"")

            self.assertEqual(check(empty), [])

    def test_a_directory_in_the_file_list_is_skipped(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "references"
            folder.mkdir()

            self.assertEqual(check(folder), [])

    def test_a_markdown_file_holding_a_nul_is_reported_not_skipped(self) -> None:
        # Skipping it in silence hid every link in the file, while invalid UTF-8 in
        # the same position was reported.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "document.md"
            document.write_bytes(b"# doc\x00\nSee [missing](gone.md).\n")

            errors = check(document)

        self.assertEqual([error.message for error in errors], ["Markdown file must be text"])

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


class WrittenCountTests(unittest.TestCase):
    # The counts below are composed from parts so this file does not carry the pattern
    # it tests for. An exemption would have been the other way, and a check its own
    # suite is exempt from is a check nothing holds to its own rule.
    EIGHT, TWO, FOUR, FIVE, THREE = "eight", "Two", "four", "5", "three"

    def workspace(self, root: Path, relative: str, body: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_a_count_of_what_the_repository_contains_is_reported(self) -> None:
        # Each of these nouns has carried a stale number: README named fewer gate steps
        # than ran, generated_block named fewer consumers than dispatched blocks,
        # PROJECT.md kept seam counts by hand. Nothing read any of them.
        for noun, number in (
            ("checks", self.EIGHT),
            ("consumers", self.TWO),
            ("seams", self.TWO),
            ("forms", self.FOUR),
        ):
            with self.subTest(noun=noun), TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = self.workspace(root, "DOC.md", f"# Doc\n\nIt has {number} {noun}.\n")

                errors = check_text.check([path], root)

                self.assertEqual(len(errors), 1, errors)
                self.assertIn("writes a count", errors[0].message)

    def test_prose_without_a_count_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.workspace(root, "DOC.md", "# Doc\n\nThe gate runs these checks.\n")

            self.assertEqual(check_text.check([path], root), [])

    def test_a_skill_states_thresholds_and_a_scenario_states_its_parameters(self) -> None:
        # A skill's rules and a recorded measurement's parameters are not claims about
        # the tree. Rewording the reps an arm was run at falsifies the record.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [
                self.workspace(
                    root,
                    "skills/x/SKILL.md",
                    f"# X\n\nWhen the scope has more than {self.FIVE} files.\n",
                ),
                self.workspace(
                    root,
                    "scripts/tests/scenarios/x/README.md",
                    f"# X\n\n{self.THREE} arms at {self.FIVE} reps each.\n",
                ),
            ]

            self.assertEqual(check_text.check(paths, root), [])

    def test_a_configured_value_is_not_a_count(self) -> None:
        # A width, a target version, a schema number: none of them say how much of
        # anything the tree holds, and none can go stale against it. Paired with a count
        # in the same file kind, so this shows where the line falls and not merely that
        # the check was quiet.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = [
                self.workspace(
                    root, "t.toml", f'line-length = 10{self.FIVE}\ntarget-version = "py310"\n'
                ),
                self.workspace(root, "s.yaml", f"schema: {self.FIVE}\n"),
            ]
            stated = self.workspace(root, "u.toml", f"# {self.TWO} consumers share it\n")

            self.assertEqual(check_text.check(allowed, root), [])
            self.assertEqual(len(check_text.check([stated], root)), 1)

    def test_a_derived_number_in_output_is_not_written_down(self) -> None:
        # The gate prints how many seams, knowns and steps it found. Those are counted
        # while it runs, so they cannot disagree with the tree. The contrast is the
        # point: computing the number is fine, stating it in the same file is not.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            computed = self.workspace(
                root, "m.py", 'print(f"OK   inventory ({len(items)} seam(s))")\n'
            )
            stated = self.workspace(root, "n.py", f'"""The inventory holds {self.TWO} seams."""\n')

            self.assertEqual(check_text.check([computed], root), [])
            self.assertEqual(len(check_text.check([stated], root)), 1)

    def test_python_and_yaml_are_read_too(self) -> None:
        # The counts that went stale were in docstrings and in a registry entry, not
        # only in Markdown.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [
                self.workspace(root, "m.py", f'"""{self.TWO} readers disagree."""\n'),
                self.workspace(root, "r.yaml", f"note: it took {self.THREE} rounds\n"),
            ]

            errors = check_text.check(paths, root)

            self.assertEqual(len(errors), 2, errors)


if __name__ == "__main__":
    unittest.main()
