# `static-review` contract inventory — micro-test (negative result)

Maintainer-only behavioral evidence. Not part of the installed skill package.
Protocol: `skills/harden-skill/references/hardening.md`.

## What was measured

Five defects across two review rounds shared one shape: *a principle the change stated, not applied
to that same change's own new work*. The hypothesis was that Phase 3's contract inventory covered
only "the invariant the change **touches**", so a principle a change **introduces** — in a commit
message or a docstring — was never inventoried and therefore never falsified. A one-clause extension
to `touches **or introduces**` was written and tested against the shipped wording.

- **Control** — the shipped Phase 3 wording
- **Treatment** — the same file with the `or introduces` clause added
- **Fixture** — `fixture/change.diff`: a change stating "both checks derive from the workspace
  rather than a maintained list" in a commit message, a module docstring, and an `AGENTS.md` rule,
  whose second check is driven by a hardcoded `NOTICE_FILES` tuple

Measure: does the output inventory that principle as a clause and falsify it against `NOTICE_FILES`?

## Result — 2026-08-25, 5 reps per arm, fresh context each, every sample read by hand

| Measure | control | treatment |
|---|---|---|
| Inventories the introduced principle and falsifies it against its own counter-example | **5 / 5** | 5 / 5 |

**The hypothesis was wrong, and the change was withdrawn.** The shipped wording already does this.
Control reps inventoried the principle from the commit message and from the module docstring, not
only from the `AGENTS.md` rule: rep 2 lists "A3 (invariant) — commit message" and "B2 (invariant) —
module docstring" as separate clauses. The `touches` / `introduces` distinction this change was
built on does not exist in practice — "stated project invariants" is already read that widely.

Control also went further than the treatment arm in places. Rep 3 pulled
`scripts/workspace_files.py:5-8` and `PROJECT.md:57-58` in as pre-existing invariants the change
touches, and used them as falsifiers against the fixture's tree-walk.

## What the treatment did add, and why it was not enough

Treatment rep 5 used the new clause as a **search heuristic**, quoting it to predict where the
counter-example would be: "its first counter-example is expected beside it: the second place the
author had to apply it. That is `check_notice_banners`." The path is shorter. The result is the
same, and the rubric fixed before the run had no allowance for a shorter path. Adding one afterward
would be the very move this repository keeps catching itself at.

## What this changes about the five original defects

They were not a gap in the skill. Nothing ran `static-review` against those changes — the reviews
were ad-hoc adversarial passes. Phase 4b's track would have caught them, which is what these ten
samples demonstrate. The missing step was application, not wording.

## Limitation

The fixture states its principle in three places, one of them `AGENTS.md`, which makes it an
invariant the change *touches* as well as one it introduces. That weakens the isolation the test was
designed for. It does not rescue the withdrawn change: control inventoried the commit-message and
docstring statements as clauses in their own right, which is the case the isolation was meant to
probe.
