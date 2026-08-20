from __future__ import annotations

import unittest

from skill_yaml import (
    Shape,
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
            ('""', ""),
        ):
            with self.subTest(value=value):
                self.assertEqual(clean_yaml_scalar(value), expected)

    def test_only_one_pair_is_removed_and_only_when_it_matches(self) -> None:
        """Trimming characters lost the closing quote of a plain scalar that ends in one."""
        for value, expected in (
            ('Use when the user asks "why"', 'Use when the user asks "why"'),
            ("\"mismatched'", "\"mismatched'"),
            ("''''value''''", "'''value'''"),
            ('He said "go" now', 'He said "go" now'),
            ('"', '"'),
        ):
            with self.subTest(value=value):
                self.assertEqual(clean_yaml_scalar(value), expected)


class MappingTests(unittest.TestCase):
    def test_a_child_scalar_reads_through_its_parent(self) -> None:
        read = get_yaml_mapping_value(MANIFEST, "resources", "references")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.value, "references/")

    def test_an_absent_child_is_absent(self) -> None:
        read = get_yaml_mapping_value(MANIFEST, "resources", "assets")

        self.assertIs(read.shape, Shape.ABSENT)
        self.assertIsNone(read.value)

    def test_an_absent_parent_is_absent(self) -> None:
        self.assertIs(
            get_yaml_mapping_value(MANIFEST, "compatibility", "hosts").shape, Shape.ABSENT
        )

    def test_a_sibling_top_level_key_ends_the_parent(self) -> None:
        text = "resources:\n  references: references/\nentrypoint: SKILL.md\n"

        self.assertIs(get_yaml_mapping_value(text, "resources", "entrypoint").shape, Shape.ABSENT)

    def test_a_child_holding_a_nested_block_is_unread_not_absent(self) -> None:
        """The defect this state exists for: a resources key naming nothing was skipped."""
        text = "resources:\n  scripts:\n    path: helpers\n"
        read = get_yaml_mapping_value(text, "resources", "scripts")

        self.assertIs(read.shape, Shape.UNREAD)
        self.assertIsNone(read.value)

    def test_a_child_with_an_empty_value_is_unread(self) -> None:
        self.assertIs(
            get_yaml_mapping_value("resources:\n  scripts:\n", "resources", "scripts").shape,
            Shape.UNREAD,
        )

    def test_a_child_declared_twice_is_unread_as_the_list_reader_answers_it(self) -> None:
        text = "resources:\n  scripts: first/\n  scripts: second/\n"
        read = get_yaml_mapping_value(text, "resources", "scripts")

        self.assertIs(read.shape, Shape.UNREAD)
        self.assertIsNone(read.value)


class ListTests(unittest.TestCase):
    def test_a_block_list_reads_every_item_in_order(self) -> None:
        read = get_yaml_list(MANIFEST, "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(
            read.items,
            ("user asks for the example", "user asks for the other example"),
        )

    def test_an_absent_key_is_absent_not_an_empty_list(self) -> None:
        read = get_yaml_list(MANIFEST, "compatibility")

        self.assertIs(read.shape, Shape.ABSENT)
        self.assertEqual(read.items, ())

    def test_a_sibling_top_level_key_ends_the_list(self) -> None:
        text = "triggers:\n  - only item\nresources:\n  - not a trigger\n"
        read = get_yaml_list(text, "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("only item",))

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        text = "triggers:\n  # a comment\n\n  - only item\n"
        read = get_yaml_list(text, "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("only item",))

    def test_a_nested_mapping_is_unread_not_the_key_own_list(self) -> None:
        """The defect this state exists for: a nested item satisfied "list of strings"."""
        text = "triggers:\n  examples:\n    - phantom\n"
        read = get_yaml_list(text, "triggers")

        self.assertIs(read.shape, Shape.UNREAD)

    def test_items_at_mixed_indentation_are_unread(self) -> None:
        text = "triggers:\n  - two\n    - four\n"

        self.assertIs(get_yaml_list(text, "triggers").shape, Shape.UNREAD)

    def test_a_nested_list_after_a_real_item_does_not_join_it(self) -> None:
        text = "triggers:\n  - real\n  nested:\n    - leaked\n"
        read = get_yaml_list(text, "triggers")

        self.assertIs(read.shape, Shape.UNREAD)
        self.assertNotIn("leaked", read.items)

    def test_a_same_line_scalar_is_not_a_list(self) -> None:
        self.assertIs(get_yaml_list("triggers: one string\n", "triggers").shape, Shape.UNREAD)

    def test_a_tab_indented_item_is_unread_because_yaml_forbids_tab_indentation(self) -> None:
        self.assertIs(get_yaml_list("triggers:\n\t- tabbed\n", "triggers").shape, Shape.UNREAD)

    def test_a_key_declared_twice_is_unread(self) -> None:
        text = "triggers:\n  - first\ntriggers:\n  - second\n"

        self.assertIs(get_yaml_list(text, "triggers").shape, Shape.UNREAD)

    def test_an_empty_block_is_unread_rather_than_an_empty_list(self) -> None:
        text = "triggers:\nentrypoint: SKILL.md\n"

        self.assertIs(get_yaml_list(text, "triggers").shape, Shape.UNREAD)

    def test_a_continuation_line_folds_into_its_item(self) -> None:
        """A multi-line plain scalar is ordinary YAML; refusing it would reject a
        manifest the ecosystem accepts."""
        text = "triggers:\n  - a very long trigger that\n    continues on the next line\n"
        read = get_yaml_list(text, "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("a very long trigger that continues on the next line",))

    def test_a_continuation_that_opens_a_mapping_is_unread(self) -> None:
        """A plain scalar may not hold ": " on any line, so this is not a continuation."""
        text = "triggers:\n  - a very long trigger\n    including: dates\n"

        self.assertIs(get_yaml_list(text, "triggers").shape, Shape.UNREAD)

    def test_an_item_that_is_a_mapping_is_unread(self) -> None:
        """The schema calls triggers a list of strings, and `- name: x` is a mapping."""
        for text in (
            "triggers:\n  - name: x\n  - name: y\n",
            "triggers:\n  - trailing:\n",
        ):
            with self.subTest(text=text):
                self.assertIs(get_yaml_list(text, "triggers").shape, Shape.UNREAD)

    def test_a_colon_that_does_not_open_a_mapping_keeps_the_item_a_string(self) -> None:
        for text, expected in (
            ("triggers:\n  - user asks for a 1:1 summary\n", "user asks for a 1:1 summary"),
            ('triggers:\n  - "user asks: summarize"\n', "user asks: summarize"),
        ):
            with self.subTest(text=text):
                read = get_yaml_list(text, "triggers")

                self.assertIs(read.shape, Shape.READ)
                self.assertEqual(read.items, (expected,))


class ReaderContractTests(unittest.TestCase):
    """One assertion per reader that it does not substitute a reading of its own."""

    DECLARED_UNREADABLY = "triggers:\n  examples:\n    - phantom\nresources:\n  scripts:\n"

    def test_a_list_reader_separates_absent_from_declared_unreadably(self) -> None:
        self.assertIs(get_yaml_list(self.DECLARED_UNREADABLY, "triggers").shape, Shape.UNREAD)
        self.assertIs(get_yaml_list(self.DECLARED_UNREADABLY, "absent").shape, Shape.ABSENT)

    def test_a_mapping_reader_separates_absent_from_declared_unreadably(self) -> None:
        unread = get_yaml_mapping_value(self.DECLARED_UNREADABLY, "resources", "scripts")
        absent = get_yaml_mapping_value(self.DECLARED_UNREADABLY, "resources", "assets")

        self.assertIs(unread.shape, Shape.UNREAD)
        self.assertIs(absent.shape, Shape.ABSENT)

    def test_a_scalar_cleaner_returns_text_it_cannot_parse_as_declared(self) -> None:
        for value in ('ends in a quote"', "\"unmatched'", "'"):
            with self.subTest(value=value):
                self.assertEqual(clean_yaml_scalar(value), value)

    def test_declaration_readers_answer_about_declaration_only(self) -> None:
        text = "entrypoint:\ntriggers:\n  - user asks\n"

        self.assertTrue(declares_key(text, "entrypoint"))
        self.assertFalse(declares_value(text, "entrypoint"))

    def test_a_top_level_key_declared_without_a_value_is_not_yet_three_state(self) -> None:
        """The one reader the contract does not yet cover; see the module docstring."""
        text = "entrypoint:\ntriggers:\n  - user asks\n"

        self.assertIsNone(get_top_level_yaml_value(text, "entrypoint"))
        self.assertIsNone(get_top_level_yaml_value(text, "absent"))


if __name__ == "__main__":
    unittest.main()
