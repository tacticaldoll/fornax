from __future__ import annotations

import unittest

from skill_yaml import (
    Document,
    Shape,
    Unreadable,
    declares_key,
    declares_value,
    get_top_level_yaml_value,
    get_yaml_list,
    get_yaml_mapping_value,
    parse,
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


class DocumentStateTests(unittest.TestCase):
    def test_a_document_holds_a_mapping_or_a_reason_and_never_both(self) -> None:
        # The pair of optional fields was freely constructible, so both of these were
        # states the type admitted and no code meant.
        with self.assertRaises(ValueError):
            Document(None, None)
        with self.assertRaises(ValueError):
            Document({}, "error")

    def test_reaching_the_mapping_of_an_unreadable_document_raises(self) -> None:
        # The docstring said a caller holding the result could not skip the failure.
        # It could: skill_graph read a family straight out of an unreadable manifest
        # and reported the family missing. A reader gets no answer now.
        document = parse('name: "unterminated\n')

        self.assertIsNotNone(document.reason)
        with self.assertRaises(Unreadable):
            declares_key(document, "name")
        with self.assertRaises(Unreadable):
            get_yaml_list(document, "triggers")


class DeclarationTests(unittest.TestCase):
    def test_a_quoted_key_is_declared(self) -> None:
        # `"name": example` is an ordinary quoted key every parser reads. A regex over
        # the source line said absent, and "declared as something else" reported as
        # "never declared" is the substitution this module's contract forbids — made
        # by the very functions the contract had named as having nothing to substitute.
        text = '"name": example\n"triggers":\n  - user asks\n'

        self.assertTrue(declares_key(parse(text), "name"))
        self.assertTrue(declares_value(parse(text), "name"))
        self.assertTrue(declares_key(parse(text), "triggers"))
        self.assertEqual(get_top_level_yaml_value(parse(text), "name"), "example")

    def test_a_key_holding_a_block_declares_no_scalar(self) -> None:
        # Answering yes here would put the caller back where it was: declaration seen,
        # the value not a string, and the check after it silently skipped.
        self.assertFalse(declares_value(parse("entrypoint:\n  - a\n"), "entrypoint"))

    def test_a_block_key_is_declared_without_a_same_line_value(self) -> None:
        self.assertTrue(declares_key(parse(MANIFEST), "triggers"))
        self.assertFalse(declares_value(parse(MANIFEST), "triggers"))

    def test_a_same_line_value_is_both_declared_and_valued(self) -> None:
        self.assertTrue(declares_key(parse(MANIFEST), "name"))
        self.assertTrue(declares_value(parse(MANIFEST), "name"))

    def test_an_absent_key_is_neither(self) -> None:
        self.assertFalse(declares_key(parse(MANIFEST), "compatibility"))
        self.assertFalse(declares_value(parse(MANIFEST), "compatibility"))

    def test_an_empty_key_does_not_borrow_the_line_beneath_it(self) -> None:
        """The `[^\\S\\n]` rule: an empty entrypoint once reported "not found: triggers:"."""
        text = "entrypoint:\ntriggers:\n  - user asks for the example\n"

        self.assertTrue(declares_key(parse(text), "entrypoint"))
        self.assertFalse(declares_value(parse(text), "entrypoint"))


class ScalarTests(unittest.TestCase):
    def test_a_top_level_scalar_round_trips(self) -> None:
        self.assertEqual(get_top_level_yaml_value(parse(MANIFEST), "family"), "meta")
        self.assertEqual(
            get_top_level_yaml_value(parse(MANIFEST), "description"),
            "Use when an agent needs the example.",
        )

    def test_an_absent_top_level_key_reads_as_none(self) -> None:
        self.assertIsNone(get_top_level_yaml_value(parse(MANIFEST), "compatibility"))

    def test_quoting_is_the_parser_s_and_a_plain_scalar_keeps_its_quotes(self) -> None:
        # Trimming quote *characters* could not tell a quoted scalar from a plain one
        # that happens to end in a quote, so `Use when the user asks "why"` came back
        # without its closing quote. The parser that owns the grammar answers both.
        for raw, expected in (
            ('"quoted"', "quoted"),
            ("'quoted'", "quoted"),
            ("  spaced  ", "spaced"),
            ("plain", "plain"),
            ('Use when the user asks "why"', 'Use when the user asks "why"'),
            ('He said "go" now', 'He said "go" now'),
            ('ends in a quote"', 'ends in a quote"'),
        ):
            with self.subTest(raw=raw):
                value = get_top_level_yaml_value(parse(f"description: {raw}\n"), "description")
                self.assertEqual(value, expected)

    def test_quoting_that_does_not_close_is_refused_not_guessed(self) -> None:
        # The cleaner returned these as declared, which reads a malformed manifest as
        # though its text were the value. They are not YAML, so there is no value.
        for raw in ("\"mismatched'", '"', "'"):
            with self.subTest(raw=raw):
                self.assertIsNotNone(parse(f"description: {raw}\n").reason)


class MappingTests(unittest.TestCase):
    def test_a_child_scalar_reads_through_its_parent(self) -> None:
        read = get_yaml_mapping_value(parse(MANIFEST), "resources", "references")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.value, "references/")

    def test_an_absent_child_is_absent(self) -> None:
        read = get_yaml_mapping_value(parse(MANIFEST), "resources", "assets")

        self.assertIs(read.shape, Shape.ABSENT)
        self.assertIsNone(read.value)

    def test_an_absent_parent_is_absent(self) -> None:
        self.assertIs(
            get_yaml_mapping_value(parse(MANIFEST), "compatibility", "hosts").shape, Shape.ABSENT
        )

    def test_a_sibling_top_level_key_ends_the_parent(self) -> None:
        text = "resources:\n  references: references/\nentrypoint: SKILL.md\n"

        read_value = get_yaml_mapping_value(parse(text), "resources", "entrypoint")

        self.assertIs(read_value.shape, Shape.ABSENT)

    def test_a_child_holding_a_nested_block_is_unread_not_absent(self) -> None:
        """The defect this state exists for: a resources key naming nothing was skipped."""
        text = "resources:\n  scripts:\n    path: helpers\n"
        read = get_yaml_mapping_value(parse(text), "resources", "scripts")

        self.assertIs(read.shape, Shape.UNREAD)
        self.assertIsNone(read.value)

    def test_a_child_with_an_empty_value_is_unread(self) -> None:
        self.assertIs(
            get_yaml_mapping_value(parse("resources:\n  scripts:\n"), "resources", "scripts").shape,
            Shape.UNREAD,
        )

    def test_a_child_declared_twice_makes_the_document_unreadable(self) -> None:
        # A repeated key is a fact about the document, not the shape of one key, and
        # answering it as a key's Shape is the conflation that let a reader speak for
        # a document that does not parse.
        text = "resources:\n  scripts: first/\n  scripts: second/\n"

        self.assertIsNotNone(parse(text).reason)


class ListTests(unittest.TestCase):
    def test_a_block_list_reads_every_item_in_order(self) -> None:
        read = get_yaml_list(parse(MANIFEST), "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(
            read.items,
            ("user asks for the example", "user asks for the other example"),
        )

    def test_an_absent_key_is_absent_not_an_empty_list(self) -> None:
        read = get_yaml_list(parse(MANIFEST), "compatibility")

        self.assertIs(read.shape, Shape.ABSENT)
        self.assertEqual(read.items, ())

    def test_a_sibling_top_level_key_ends_the_list(self) -> None:
        text = "triggers:\n  - only item\nresources:\n  - not a trigger\n"
        read = get_yaml_list(parse(text), "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("only item",))

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        text = "triggers:\n  # a comment\n\n  - only item\n"
        read = get_yaml_list(parse(text), "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("only item",))

    def test_a_nested_mapping_is_unread_not_the_key_own_list(self) -> None:
        """The defect this state exists for: a nested item satisfied "list of strings"."""
        text = "triggers:\n  examples:\n    - phantom\n"
        read = get_yaml_list(parse(text), "triggers")

        self.assertIs(read.shape, Shape.UNREAD)

    def test_a_line_indented_past_the_items_continues_the_one_above(self) -> None:
        # The hand-written reader called this mixed indentation and declined it. YAML
        # folds a more-indented line into the plain scalar above, so it is one item
        # reading "two - four" — and declining it refused a manifest every parser in
        # the ecosystem accepts, which is the one thing this module must not do.
        read = get_yaml_list(parse("triggers:\n  - two\n    - four\n"), "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("two - four",))

    def test_a_nested_list_after_a_real_item_makes_the_document_unreadable(self) -> None:
        # A sequence entry and a mapping entry cannot be siblings, so nothing here is
        # a list whose items could leak — the document is what fails.
        text = "triggers:\n  - real\n  nested:\n    - leaked\n"

        self.assertIsNotNone(parse(text).reason)

    def test_a_same_line_scalar_is_not_a_list(self) -> None:
        found = get_yaml_list(parse("triggers: one string\n"), "triggers")

        self.assertIs(found.shape, Shape.UNREAD)

    def test_a_tab_indented_item_makes_the_document_unreadable(self) -> None:
        self.assertIsNotNone(parse("triggers:\n\t- tabbed\n").reason)

    def test_a_key_declared_twice_makes_the_document_unreadable(self) -> None:
        text = "triggers:\n  - first\ntriggers:\n  - second\n"

        self.assertIsNotNone(parse(text).reason)

    def test_an_empty_block_is_unread_rather_than_an_empty_list(self) -> None:
        text = "triggers:\nentrypoint: SKILL.md\n"

        self.assertIs(get_yaml_list(parse(text), "triggers").shape, Shape.UNREAD)

    def test_a_continuation_line_folds_into_its_item(self) -> None:
        """A multi-line plain scalar is ordinary YAML; refusing it would reject a
        manifest the ecosystem accepts."""
        text = "triggers:\n  - a very long trigger that\n    continues on the next line\n"
        read = get_yaml_list(parse(text), "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("a very long trigger that continues on the next line",))

    def test_a_continuation_that_opens_a_mapping_makes_the_document_unreadable(self) -> None:
        """A plain scalar may not hold ": " on any line, so this is not a continuation."""
        text = "triggers:\n  - a very long trigger\n    including: dates\n"

        self.assertIsNotNone(parse(text).reason)

    def test_an_item_that_is_a_mapping_is_unread(self) -> None:
        """The schema calls triggers a list of strings, and `- name: x` is a mapping."""
        for text in (
            "triggers:\n  - name: x\n  - name: y\n",
            "triggers:\n  - trailing:\n",
        ):
            with self.subTest(text=text):
                self.assertIs(get_yaml_list(parse(text), "triggers").shape, Shape.UNREAD)

    def test_a_colon_that_does_not_open_a_mapping_keeps_the_item_a_string(self) -> None:
        for text, expected in (
            ("triggers:\n  - user asks for a 1:1 summary\n", "user asks for a 1:1 summary"),
            ('triggers:\n  - "user asks: summarize"\n', "user asks: summarize"),
        ):
            with self.subTest(text=text):
                read = get_yaml_list(parse(text), "triggers")

                self.assertIs(read.shape, Shape.READ)
                self.assertEqual(read.items, (expected,))


class MappingReaderShapeTests(unittest.TestCase):
    """Shapes the mapping reader steps over rather than misreading."""

    def test_comments_and_blank_lines_under_the_parent_are_skipped(self) -> None:
        text = "resources:\n  # a note\n\n  scripts: helpers/\n"
        read = get_yaml_mapping_value(parse(text), "resources", "scripts")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.value, "helpers/")

    def test_a_stray_line_beside_a_child_makes_the_document_unreadable(self) -> None:
        # The hand-written reader skipped the line for having no colon and read the
        # child beside it. A scalar and a mapping entry cannot be siblings, so this is
        # not YAML at all, and reading a value out of it read past a malformed
        # document rather than saying it was one.
        text = "resources:\n  stray\n  scripts: helpers/\n"

        self.assertIsNotNone(parse(text).reason)

    def test_a_key_carrying_both_a_scalar_and_items_is_unread(self) -> None:
        # Without the same-line check the items alone would read as the key's list,
        # so a document YAML rejects would come back as a value.
        self.assertIs(
            get_yaml_list(parse("triggers: scalar\n  - a\n"), "triggers").shape, Shape.UNREAD
        )


class ReaderContractTests(unittest.TestCase):
    """One assertion per reader that it does not substitute a reading of its own."""

    DECLARED_UNREADABLY = "triggers:\n  examples:\n    - phantom\nresources:\n  scripts:\n"

    def test_a_list_reader_separates_absent_from_declared_unreadably(self) -> None:
        document = parse(self.DECLARED_UNREADABLY)

        self.assertIs(get_yaml_list(document, "triggers").shape, Shape.UNREAD)
        self.assertIs(get_yaml_list(document, "absent").shape, Shape.ABSENT)

    def test_a_mapping_reader_separates_absent_from_declared_unreadably(self) -> None:
        unread = get_yaml_mapping_value(parse(self.DECLARED_UNREADABLY), "resources", "scripts")
        absent = get_yaml_mapping_value(parse(self.DECLARED_UNREADABLY), "resources", "assets")

        self.assertIs(unread.shape, Shape.UNREAD)
        self.assertIs(absent.shape, Shape.ABSENT)

    def test_a_repeated_key_is_refused_rather_than_resolved(self) -> None:
        # Both PyYAML loaders take the last one silently. The readers this replaced
        # answered UNREAD for a repeated key, and adopting a parser must not lose a
        # guarantee the hand-written code had. The refusal reaches nested keys too.
        self.assertIsNotNone(parse("triggers:\n  - a\ntriggers:\n  - b\n").reason)
        self.assertIsNotNone(parse("resources:\n  scripts: a\n  scripts: b\n").reason)

    def test_a_key_this_cannot_compare_is_a_diagnostic_not_a_crash(self) -> None:
        # YAML admits a complex key, `? [a, b]`, and constructing one gives a list.
        # Testing set membership with it raised TypeError out of a function whose
        # caller was promised a reason.
        self.assertIsNotNone(parse("? [a, b]\n: value\n").reason)

    def test_yaml_1_1_types_do_not_change_what_a_manifest_says(self) -> None:
        # safe_load reads a trigger written `1:1` as the integer 61, `no` as False and
        # `007` as 7. A reader that changes what a manifest says is the substitution
        # this module's contract forbids, arriving from the library instead of a regex.
        read = get_yaml_list(parse("triggers:\n  - 1:1\n  - no\n  - 007\n"), "triggers")

        self.assertIs(read.shape, Shape.READ)
        self.assertEqual(read.items, ("1:1", "no", "007"))

    def test_declaration_readers_answer_about_declaration_only(self) -> None:
        text = "entrypoint:\ntriggers:\n  - user asks\n"

        self.assertTrue(declares_key(parse(text), "entrypoint"))
        self.assertFalse(declares_value(parse(text), "entrypoint"))

    def test_a_top_level_key_declared_without_a_value_is_not_yet_three_state(self) -> None:
        """The one reader the contract does not yet cover; see the module docstring."""
        text = "entrypoint:\ntriggers:\n  - user asks\n"

        self.assertIsNone(get_top_level_yaml_value(parse(text), "entrypoint"))
        self.assertIsNone(get_top_level_yaml_value(parse(text), "absent"))


if __name__ == "__main__":
    unittest.main()
