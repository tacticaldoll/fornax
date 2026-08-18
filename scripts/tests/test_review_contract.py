from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COVERAGE_SETS = (
    "gate-reviewed:",
    "partially-gate-reviewed:",
    "triage-only:",
    "unread:",
)


class ReviewContractTests(unittest.TestCase):
    def test_producer_template_always_enumerates_all_coverage_sets(self) -> None:
        skill = (ROOT / "skills/static-review/SKILL.md").read_text(encoding="utf-8")
        coverage = next(line for line in skill.splitlines() if line.startswith("**Coverage**:"))
        for label in COVERAGE_SETS:
            with self.subTest(label=label):
                self.assertIn(label, coverage)

    def test_consumer_requires_the_relevant_gate_for_partial_coverage(self) -> None:
        skill = (ROOT / "skills/triage-findings/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`partially-gate-reviewed` with the relevant", skill)
        self.assertIn("opened gates omit the relevant gate cannot close", skill)

    def test_cross_round_review_records_enumerate_all_coverage_sets(self) -> None:
        records = sorted(
            (ROOT / "scripts/tests/scenarios/triage-findings/crossround").glob(
                "*/records/review-record.md"
            )
        )
        self.assertTrue(records)
        for record in records:
            coverage = next(
                line
                for line in record.read_text(encoding="utf-8").splitlines()
                if line.startswith("**Coverage**:")
            )
            for label in COVERAGE_SETS:
                with self.subTest(record=record, label=label):
                    self.assertIn(label, coverage)

    def test_foreign_or_pre_rule_fixture_remains_the_unenumerated_compatibility_case(self) -> None:
        record = ROOT / "scripts/tests/scenarios/triage-findings/review-record.md"
        content = record.read_text(encoding="utf-8")
        coverage = next(line for line in content.splitlines() if line.startswith("**Coverage**:"))

        self.assertIn("foreign or pre-rule", content)
        for label in COVERAGE_SETS:
            with self.subTest(label=label):
                self.assertNotIn(label, coverage)


if __name__ == "__main__":
    unittest.main()
