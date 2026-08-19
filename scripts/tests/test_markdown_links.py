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
                'reference file.md "Guide"',
                "reference%20file.md",
            ),
            "balanced destination": (
                "[guide](reference(one(two)).md)",
                "reference(one(two)).md",
                "reference(one(two)).md",
            ),
            "escaped destination punctuation": (
                r"[guide](reference\(local\).md)",
                "reference(local).md",
                "reference(local).md",
            ),
            "parenthesized title": (
                "[guide](README.md (overview))",
                'README.md "overview"',
                "README.md",
            ),
            "padded destination": (
                "[guide]( README.md )",
                "README.md",
                "README.md",
            ),
        }
        for label, (text, shown_target, destination) in cases.items():
            with self.subTest(label=label):
                self.assertEqual(
                    list(markdown_links.iter_markdown_links(text)),
                    [markdown_links.MarkdownLink(shown_target, destination)],
                )

    def test_local_target_strips_fragments_and_excludes_external_links(self) -> None:
        self.assertEqual(markdown_links.local_target("docs/guide.md#usage"), "docs/guide.md")
        self.assertEqual(
            markdown_links.local_target("docs/guide.md?raw=1#usage"),
            "docs/guide.md",
        )
        self.assertIsNone(markdown_links.local_target("#usage"))
        self.assertIsNone(markdown_links.local_target("https://example.com/guide"))
        self.assertIsNone(markdown_links.local_target("//example.com/guide"))

    def test_percent_encoded_fragment_marker_remains_part_of_the_path(self) -> None:
        link = next(markdown_links.iter_markdown_links("[guide](target%23part.md)"))

        self.assertEqual(link.shown_target, "target#part.md")
        self.assertEqual(link.destination, "target%23part.md")
        self.assertEqual(markdown_links.local_target(link.destination), "target#part.md")

        self.assertEqual(markdown_links.local_target("target%3Fpart.md"), "target?part.md")

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

    def test_reference_definitions_do_not_leak_between_documents(self) -> None:
        self.assertEqual(
            tuple(
                link.destination
                for link in markdown_links.iter_markdown_links(
                    "[guide][reference]\n\n[reference]: first.md"
                )
            ),
            ("first.md",),
        )
        self.assertEqual(
            list(markdown_links.iter_markdown_links("[guide][reference]")),
            [],
        )

    def test_block_context_conformance(self) -> None:
        cases = {
            "code span stops at paragraph boundary": (
                "` lone\n\n[guide](outside.md)\n\n` later",
                ("outside.md",),
            ),
            "backtick fence is literal across blank lines": (
                "```md\n\n[example](inside.md)\n```\n\n[guide](outside.md)",
                ("outside.md",),
            ),
            "tilde fence is literal": (
                "~~~md\n[example](inside.md)\n~~~",
                (),
            ),
            "unclosed fence is literal to end of document": (
                "```md\n[example](inside.md)",
                (),
            ),
            "indented code block is literal": (
                "    [example](inside.md)\n\n[guide](outside.md)",
                ("outside.md",),
            ),
            "indentation cannot interrupt a paragraph": (
                "paragraph\n    [guide](continuation.md)",
                ("continuation.md",),
            ),
            "common prose containers retain links": (
                "# [heading](heading.md)\n- [item](item.md)\n> [quote](quote.md)",
                ("heading.md", "item.md", "quote.md"),
            ),
            "code spans do not cross heading boundaries": (
                "# ` heading\n[guide](outside.md)\n` later",
                ("outside.md",),
            ),
            "code spans do not cross list item boundaries": (
                "- ` first\n- [guide](outside.md)\n- ` third",
                ("outside.md",),
            ),
            "nested fenced blocks remain literal": (
                "- ```md\n  [example](inside.md)\n  ```\n\n[guide](outside.md)",
                ("outside.md",),
            ),
            "reference links resolve through definitions": (
                "[guide][reference]\n\n[reference]: reference.md",
                ("reference.md",),
            ),
            "linked images expose both local targets": (
                "[![image](image.png)](page.md)",
                ("page.md", "image.png"),
            ),
        }
        for label, (text, destinations) in cases.items():
            with self.subTest(label=label):
                self.assertEqual(
                    tuple(link.destination for link in markdown_links.iter_markdown_links(text)),
                    destinations,
                )
