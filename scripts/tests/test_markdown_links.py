from __future__ import annotations

import unittest

import markdown_links


class MarkdownLinksTests(unittest.TestCase):
    def test_parses_supported_destinations_and_titles(self) -> None:
        cases = {
            "quoted title with parentheses": (
                '[guide](README.md "short (local) guide")',
                'README.md "short (local) guide"',
                "README.md",
            ),
            "escaped title quote": (
                '[guide](README.md "the \\"local\\" guide")',
                'README.md "the \\"local\\" guide"',
                "README.md",
            ),
            "angle destination": (
                '[guide](<reference file.md> "Guide")',
                '<reference file.md> "Guide"',
                "reference file.md",
            ),
            "balanced destination": (
                "[guide](reference(one(two)).md)",
                "reference(one(two)).md",
                "reference(one(two)).md",
            ),
            "escaped destination punctuation": (
                r"[guide](reference\(local\).md)",
                r"reference\(local\).md",
                "reference(local).md",
            ),
            "parenthesized title": (
                "[guide](README.md (short (local) guide))",
                "README.md (short (local) guide)",
                "README.md",
            ),
        }
        for label, (text, raw_target, destination) in cases.items():
            with self.subTest(label=label):
                self.assertEqual(
                    list(markdown_links.iter_markdown_links(text)),
                    [markdown_links.MarkdownLink(raw_target, destination)],
                )

    def test_local_target_strips_fragments_and_excludes_external_links(self) -> None:
        self.assertEqual(markdown_links.local_target("docs/guide.md#usage"), "docs/guide.md")
        self.assertIsNone(markdown_links.local_target("#usage"))
        self.assertIsNone(markdown_links.local_target("https://example.com/guide"))

    def test_malformed_links_are_not_partial_matches(self) -> None:
        cases = (
            '[guide](README.md "unterminated)',
            "[guide](reference(unbalanced.md)",
            "[guide](<reference file.md)",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(list(markdown_links.iter_markdown_links(text)), [])

    def test_escaped_and_nested_labels_are_links(self) -> None:
        cases = (
            r"[doc \] page](missing.md)",
            "[doc [local] page](missing.md)",
            "[doc `local` page](missing.md)",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    list(markdown_links.iter_markdown_links(text)),
                    [markdown_links.MarkdownLink("missing.md", "missing.md")],
                )

    def test_escaped_label_openers_and_code_spans_are_not_links(self) -> None:
        cases = (
            r"\[example](missing.md)",
            "`[example](missing.md)`",
            "`` `[example](missing.md)` ``",
            "before `code\n[example](missing.md)` after",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(list(markdown_links.iter_markdown_links(text)), [])

    def test_unmatched_backticks_do_not_hide_a_later_link(self) -> None:
        self.assertEqual(
            list(markdown_links.iter_markdown_links("` unmatched [example](missing.md)")),
            [markdown_links.MarkdownLink("missing.md", "missing.md")],
        )

    def test_link_syntax_inside_a_title_is_not_a_second_link(self) -> None:
        self.assertEqual(
            list(
                markdown_links.iter_markdown_links(
                    '[guide](README.md "see [example](missing.md)")'
                )
            ),
            [
                markdown_links.MarkdownLink(
                    'README.md "see [example](missing.md)"', "README.md"
                )
            ],
        )
