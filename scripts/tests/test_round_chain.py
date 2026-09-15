"""Cover the round chain against the shapes its corpus actually holds.

The filename grammar is this repository's own, so it carries the two negative controls
`AGENTS.md` asks of a hand-written matcher: a near-miss sharing the accepted prefix, and
a valid alternate spelling of the same range. The revision halves are git's to resolve
and the field is the markdown parser's to read, so neither is controlled here.
"""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import round_chain
from agent_skill_format.read_whole import Unread

RANGE = "8d92ff7..1e37d86"
FIELD = "**Prior round**: `docs/dispositions/d12997d..7c88454.md`\n"


def history(
    *heads: str,
    off_branch: tuple[str, ...] = (),
    aliases: dict[str, str] | None = None,
) -> round_chain.History:
    """Place *heads* on a branch, newest first, as `git rev-list` reports them.

    A revision in *off_branch* resolves to a commit the branch does not carry, which
    is the absence that reads alike as one nothing resolves at all until asked apart.
    """
    resolved = {head: f"full-{head}" for head in (*heads, *off_branch)}
    for spelling, meant in (aliases or {}).items():
        resolved[spelling] = f"full-{meant}"
    return round_chain.History(
        order={f"full-{head}": position for position, head in enumerate(heads)},
        resolved=resolved,
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
        self.assertEqual(
            round_chain.prior_field(FIELD), "docs/dispositions/d12997d..7c88454.md"
        )

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
            round_chain.names_for(reading, [reading, second], history("b", "a")),
            {
                "docs/dispositions/a..b.md",
                f"docs/dispositions/a..b.{round_chain.SECOND_READING}.md",
            },
        )

    def test_one_range_spelled_two_ways_is_one_round(self) -> None:
        # The halves resolve to the same commits and are written differently, which is
        # what a full object name beside an abbreviation looks like. Comparing the text
        # made this two rounds and failed the round after it.
        reading = record("a..b.md")
        second = record(f"aaaa..bbbb.{round_chain.SECOND_READING}.md")
        settled = history("b", "a", aliases={"aaaa": "a", "bbbb": "b"})
        self.assertEqual(
            round_chain.names_for(reading, [reading, second], settled),
            {
                "docs/dispositions/a..b.md",
                f"docs/dispositions/aaaa..bbbb.{round_chain.SECOND_READING}.md",
            },
        )

    def test_a_field_naming_another_directory_is_not_accepted(self) -> None:
        # The same last segment under a directory the chain does not run through. Read
        # as a bare name it was indistinguishable from a disposition.
        reading = record("a..b.md")
        accepted = round_chain.names_for(reading, [reading], history("b"))
        self.assertNotIn("docs/reviews/a..b.md", accepted)

    def test_a_head_the_branch_does_not_hold_leaves_the_chain(self) -> None:
        records = [record("a..b.md"), record("b..c.md")]
        self.assertEqual(round_chain.neighbours(records, history("b")), [])


class AbsenceTests(TestCase):
    def test_a_revision_nothing_resolves_says_so(self) -> None:
        absent = history("b").place("c")
        self.assertIsInstance(absent, round_chain.Unresolved)
        self.assertIn("resolves to no commit", str(absent))

    def test_a_revision_the_branch_does_not_hold_says_so_differently(self) -> None:
        # Same shape as the case above and a different repair: this revision exists
        # and was written somewhere else, so a reader sent to look on the branch for
        # it finds nothing and learns nothing.
        elsewhere = history("b", off_branch=("c",)).place("c")
        self.assertIsInstance(elsewhere, round_chain.OffBranch)
        self.assertIn("does not hold", str(elsewhere))

    def test_a_revision_the_branch_holds_places_it(self) -> None:
        self.assertEqual(history("b", "a").place("a"), 1)


class ExitTests(TestCase):
    def test_an_unreadable_branch_still_reports_what_was_already_found(self) -> None:
        # The run that can say least about the tree used to say least about its own
        # findings too: it returned before printing the names it had failed to read.
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / round_chain.RECORDS).mkdir(parents=True)
            (root / round_chain.RECORDS / "notes.md").write_text("", encoding="utf-8")
            stderr = StringIO()
            with redirect_stderr(stderr):
                result = round_chain.check(root)
        reported = stderr.getvalue()
        self.assertEqual(result, 1)
        self.assertIn("notes.md", reported)
