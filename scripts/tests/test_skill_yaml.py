from __future__ import annotations

import unittest

from skill_yaml import (
    clean_yaml_scalar,
    declares_key,
    declares_value,
    get_top_level_yaml_value,
    get_yaml_list,
    get_yaml_mapping_value,
)


MANIFEST = (
    "name: example-skill\n"
    "family: meta\n"
    "status: draft\n"
    "description: Use when an agent needs the example.\n"
    "entrypoint: SKILL.md\n"
    "triggers:\n"
    "  - user asks for the example\n"
    "  - user asks for the other example\n"
    "resources:\n"
    "  references: references/\n"
)


class DeclarationTests(unittest.TestCase):
    def test_a_block_key_is_declared_without_a_same_line_value(self) -> None:
        self.assertTrue(declares_key(MANIFEST, "triggers"))
        self.assertFalse(declares_value(MANIFEST, "triggers"))

    def test_a_same_line_value_is_both_declared_and_valued(self) -> None:
        self.assertTrue(declares_key(MANIFEST, "name"))
        self.assertTrue(declares_value(MANIFEST, "name"))

    def test_an_absent_key_is_neither(self) -> None:
        self.assertFalse(declares_key(MANIFEST, "compatibility"))
        self.assertFalse(declares_value(MANIFEST, "compatibility"))

    def test_an_empty_key_does_not_borrow_the_line_beneath_it(self) -> None:
        """The `[^\\S\\n]` rule: an empty entrypoint once reported "not found: triggers:"."""
        text = "entrypoint:\ntriggers:\n  - user asks for the example\n"

        self.assertTrue(declares_key(text, "entrypoint"))
        self.assertFalse(declares_value(text, "entrypoint"))


class ScalarTests(unittest.TestCase):
    def test_a_top_level_scalar_round_trips(self) -> None:
        self.assertEqual(get_top_level_yaml_value(MANIFEST, "family"), "meta")
        self.assertEqual(
            get_top_level_yaml_value(MANIFEST, "description"),
            "Use when an agent needs the example.",
        )

    def test_an_absent_top_level_key_reads_as_none(self) -> None:
        self.assertIsNone(get_top_level_yaml_value(MANIFEST, "compatibility"))

    def test_a_matched_quote_pair_and_surrounding_space_are_removed(self) -> None:
        for value, expected in (
            ('"quoted"', "quoted"),
            ("'quoted'", "quoted"),
            ("  spaced  ", "spaced"),
            ("plain", "plain"),
        ):
            with self.subTest(value=value):
                self.assertEqual(clean_yaml_scalar(value), expected)


class MappingTests(unittest.TestCase):
    def test_a_child_scalar_reads_through_its_parent(self) -> None:
        self.assertEqual(get_yaml_mapping_value(MANIFEST, "resources", "references"), "references/")

    def test_an_absent_child_reads_as_none(self) -> None:
        self.assertIsNone(get_yaml_mapping_value(MANIFEST, "resources", "assets"))

    def test_an_absent_parent_reads_as_none(self) -> None:
        self.assertIsNone(get_yaml_mapping_value(MANIFEST, "compatibility", "hosts"))

    def test_a_sibling_top_level_key_ends_the_parent(self) -> None:
        text = "resources:\n  references: references/\nentrypoint: SKILL.md\n"

        self.assertIsNone(get_yaml_mapping_value(text, "resources", "entrypoint"))


class ListTests(unittest.TestCase):
    def test_a_block_list_reads_every_item_in_order(self) -> None:
        self.assertEqual(
            get_yaml_list(MANIFEST, "triggers"),
            ["user asks for the example", "user asks for the other example"],
        )

    def test_an_absent_key_reads_as_no_items(self) -> None:
        self.assertEqual(get_yaml_list(MANIFEST, "compatibility"), [])

    def test_a_sibling_top_level_key_ends_the_list(self) -> None:
        text = "triggers:\n  - only item\nresources:\n  - not a trigger\n"

        self.assertEqual(get_yaml_list(text, "triggers"), ["only item"])

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        text = "triggers:\n  # a comment\n\n  - only item\n"

        self.assertEqual(get_yaml_list(text, "triggers"), ["only item"])


if __name__ == "__main__":
    unittest.main()
