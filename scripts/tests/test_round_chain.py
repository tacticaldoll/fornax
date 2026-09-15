"""Cover the round chain against the shapes its corpus actually holds.

The filename grammar is this repository's own, so it carries the two negative controls
`AGENTS.md` asks of a hand-written matcher: a near-miss sharing the accepted prefix, and
a valid alternate spelling of the same range. The revision halves are git's to resolve
and the field is the markdown parser's to read, so neither is controlled here.
"""

from unittest import TestCase

import round_chain
from agent_skill_format.read_whole import Unread

RANGE = "8d92ff7..1e37d86"
FIELD = "**Prior round**: `docs/dispositions/d12997d..7c88454.md`\n"


def history(*heads: str) -> round_chain.History:
    """Place *heads* on a branch, newest first, as `git rev-list` reports them."""
    return round_chain.History(
        order={f"full-{head}": position for position, head in enumerate(heads)},
        resolved={head: f"full-{head}" for head in heads},
    )


def record(name: str, prior: str | None = None) -> round_chain.Record:
    read = round_chain.read_record(name, f"**Prior round**: `{prior}`\n" if prior else "")
    assert isinstance(read, round_chain.Record), read
    return read


class RecordNameTests(TestCase):
    def test_a_range_reads_whole_with_its_halves_kept_apart(self) -> None:
        read = record(f"{RANGE}.md")
        self.assertEqual((read.base, read.head), ("8d92ff7", "1e37d86"))
        self.assertFalse(read.second_reading)

    def test_the_declared_suffix_is_read_as_a_second_reading(self) -> None:
        self.assertTrue(record(f"{RANGE}.{round_chain.SECOND_READING}.md").second_reading)

    def test_a_release_tag_base_carrying_dots_stays_with_the_base(self) -> None:
        read = record("v0.4.1..1609403.md")
        self.assertEqual((read.base, read.head), ("v0.4.1", "1609403"))

    def test_a_near_miss_sharing_the_accepted_prefix_is_unread(self) -> None:
        # Same range, same shape, an undeclared suffix. Admitting any suffix here is the
        # invented terminator the authoring rule refuses: it would read this as a record
        # and leave whatever the suffix meant unaccounted.
        read = round_chain.read_record(f"{RANGE}.third-reading.md", "")
        self.assertIsInstance(read, Unread)

    def test_an_alternate_spelling_of_the_same_range_still_reads(self) -> None:
        # The same meaning written the other way git accepts. A grammar that took only
        # the abbreviation would be a claim about the examples, not about the names.
        read = record("8d92ff7d9c646f13984e5ae1c2c85c7b9c85520f..1e37d86.md")
        self.assertEqual(read.head, "1e37d86")

    def test_a_name_holding_no_range_is_unread(self) -> None:
        self.assertIsInstance(round_chain.read_record("notes.md", ""), Unread)


class PriorFieldTests(TestCase):
    def test_the_field_is_read_through_its_markup(self) -> None:
        self.assertEqual(round_chain.prior_field(FIELD), "d12997d..7c88454.md")

    def test_a_record_carrying_no_field_reports_none(self) -> None:
        self.assertIsNone(round_chain.prior_field("## Disposition Record\n"))

    def test_inline_code_outside_the_field_is_not_taken_for_it(self) -> None:
        self.assertIsNone(round_chain.prior_field("**Scope**: `a..b`, derived\n"))


class ChainTests(TestCase):
    def test_rounds_pair_with_the_round_before_them(self) -> None:
        records = [record("a..b.md"), record("b..c.md"), record("c..d.md")]
        paired = round_chain.neighbours(records, history("d", "c", "b"))
        self.assertEqual(
            [(earlier.name, later.name) for earlier, later in paired],
            [("a..b.md", "b..c.md"), ("b..c.md", "c..d.md")],
        )

    def test_a_second_reading_is_not_a_link_in_the_chain(self) -> None:
        records = [
            record("a..b.md"),
            record(f"a..b.{round_chain.SECOND_READING}.md"),
            record("b..c.md"),
        ]
        paired = round_chain.neighbours(records, history("c", "b"))
        self.assertEqual(
            [(earlier.name, later.name) for earlier, later in paired],
            [("a..b.md", "b..c.md")],
        )

    def test_either_record_of_a_twice_read_round_identifies_it(self) -> None:
        reading = record("a..b.md")
        second = record(f"a..b.{round_chain.SECOND_READING}.md")
        self.assertEqual(
            round_chain.names_for(reading, [reading, second]),
            {"a..b.md", f"a..b.{round_chain.SECOND_READING}.md"},
        )

    def test_a_head_the_branch_does_not_hold_leaves_the_chain(self) -> None:
        records = [record("a..b.md"), record("b..c.md")]
        self.assertEqual(round_chain.neighbours(records, history("b")), [])
