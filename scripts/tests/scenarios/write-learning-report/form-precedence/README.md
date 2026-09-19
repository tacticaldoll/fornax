# `write-learning-report` structured-form precedence — micro-test

Maintainer-only behavioral evidence for the precedence paragraph in the Structured expression
section. Not part of the installed skill package.

## Status — 2026-09-18

Superseded as evidence for the workspace candidate's form-selection behavior: conditional
claim-to-form selection replaces the unconditional obligation these arms measured. Results below
remain records of their stated historical variants; their claims about mandatory forms do not
describe the workspace candidate. The historical baseline remains unchanged. They did not score
semantic validity or rendering hygiene, and reports were not preserved.
See [the claim-to-form scenario](claim-to-form/README.md) for the replacement experiment.

Protocol: `skills/harden-skill/references/hardening.md`, with one stated departure — 2 reps per arm
rather than the 5 or more that protocol requires, and no variance measure. The question here is
whether the conflict is reported as settled at all, which is an existence claim; a rate would need
the reps the protocol asks for and is not claimed.

## What was measured

A review found that the skill stated the four-form mandate and kept "Structure follows content" and
"Do not pad" unqualified, so a subject with no mechanism to draw met rules that answer differently
and nothing said which governs. The repair adds a paragraph assigning precedence.

The question is **not** whether the output changes. It is who settles the contradiction: the
document, or the agent reading it. A repair that leaves the agent reasoning its own way to the same
answer has not removed the contradiction, it has been lucky.

- **Control (arm A)** — the pre-change wording of `skills/write-learning-report/SKILL.md`
- **Treatment (arm B)** — the candidate wording, differing only in the precedence paragraph and
  the two scoped Rules lines
- **Fixture** — `fixture/subject.md`, a governance conversation deciding not to convert a
  never-violated prose convention into a check. Chosen because it has no mechanism to draw, no
  numbers, and no state to model: the case the mandate is hardest on

Both arms carry Phase 6, which predates this change, so the arms differ in one variable.

## Prompt

Identical for both arms except which skill file is read. Fresh context per rep, no repository access.

```text
You are executing a skill's instructions literally. Do not look for other files in the
repository; do not search the web.

1. Read the skill at <variant>/SKILL.md and treat it as your complete instructions.
2. Read the source material at <fixture>/subject.md. That conversation is the material
   to report on.
3. Follow the skill to produce the learning report it calls for. Produce it in your
   reply; write no files.

Then add a section headed `## ANSWERS`:

A. For THIS subject, is each of the four structured forms required, optional, or not
   applicable? Quote the sentence(s) you based each answer on.
B. Did you include a formal statement? If yes, paste it. If no, say which sentence
   permitted you to leave it out.
C. Did you find any two rules in the skill that give different answers about whether
   this report needs those forms? If so, quote both and say which one you followed
   and why.

Be honest in ANSWERS even if it contradicts what you produced above.
```

## Results

Round 1, 2 reps per arm, fresh context each, every sample read by hand. Raw answers in
`raw-scores.md`. Round 1 was scored without a `scoring.md`, which is why two of its rows below are
re-derived: the originals were written from the narrative rather than from the raw answers.

| Measure | A (prior wording) | B (precedence paragraph) |
|---|---|---|
| Answered all four forms required | 2 of 2 | 2 of 2 |
| Produced all four forms in the report (read at scoring time; see `scoring.md`) | 2 of 2 | 2 of 2 |
| Reported the two scoped Rules as settled by the text | 0 of 2 | 2 of 2 |
| Named a conflict it had to settle itself | 2 of 2 | 1 of 2 |

The last row is the ratio row in every case that scores it, and that row was scoped only after these
runs — so arm B's remaining one is the wording no arm has seen, not a treatment that failed.

**On this fixture, no arm's output lost a form.** Both arms produced four forms on the subject the
mandate is hardest on. Arm A rep 1 did reach for the exemption — it read "simplify structure" as
licence to drop a form — and then argued itself out of it. So a result table measuring output would
have shown nothing here, and whether the mandate binds beyond this fixture is unmeasured.

**Where the decision was made moved, at least once.** Arm B rep 1 attributes the resolution to the
document in as many words: 「我遵循的是第二組，理由不是我的判斷，而是 skill 明文指定了優先順序」.
Both arm A reps reasoned their own way there instead. Two reps per arm support that this can happen,
not how often.

## Results — round 2

The treatment after the `2c0b029..0ac59bb` round's repair: the precedence paragraph states the
property rather than a tally, names the rules it reaches, and each named rule points back at it.
Control is round 1's arm B, not re-run. 2 reps, fresh context each, scored against `scoring.md`,
which was written before these runs. Raw answers in `raw-scores-round2.md`.

| Measure | round 1, arm B (tally wording) | round 2 (property wording) |
|---|---|---|
| Answered all four forms required | 2 of 2 | 2 of 2 |
| Produced all four forms in the report (read at scoring time; see `scoring.md`) | 2 of 2 | 2 of 2 |
| Reported the two scoped Rules as settled by the text | 2 of 2 | 2 of 2 |
| Named a conflict it had to settle itself | 1 of 2 | 0 of 2 |

**The remaining self-settled conflict is gone on this fixture.** Round 1's arm B left the ratio row
outside the scoping, and one rep settled it on its own analysis. Round 2 names that row in the
paragraph and has the row point back, and neither rep reports a conflict it had to judge. Rep 1
describes its own remaining judgement as how to satisfy both rules rather than which one wins, which
the scoring counts as no.

What round 2 does not separate is the paragraph's rewording from the ratio row's inclusion; both
landed in one repair. A run against the property wording with the ratio row still unnamed was not
made, so which half moved the last measure is unmeasured.

## Results — round 3

The treatment after the `9f449a2..93c5b4b` round's repair: the mandate's opening sentence states an
output obligation, `Every report carries all four forms below`, where it had been a planning
instruction. Control is round 2, not re-run. 2 reps, fresh context each, scored against
`scoring.md`. Raw answers in `raw-scores-round3.md`.

| Measure | round 2 (planning wording) | round 3 (obligation wording) |
|---|---|---|
| Answered all four forms required | 2 of 2 | 2 of 2 |
| Produced all four forms in the report (read at scoring time; see `scoring.md`) | 2 of 2 | 2 of 2 |
| Reported the two scoped Rules as settled by the text | 2 of 2 | 2 of 2 |
| Named a conflict it had to settle itself | 0 of 2 | 0 of 2 |

**Hardening the mandate moved no measure.** The wording it replaced already bound behaviour on this
fixture, so the repair closed a reading a reader could have taken rather than one any run took. That
is what the review found it for — a sentence weaker than everything downstream assumes — not a
behaviour it was observed to produce.

**No run filled a form to satisfy the requirement**, which is the failure an unconditional mandate
invites. Each rep volunteered which of its own forms was weakest and why, and in both the weakness
was the same: an inequality whose structure the source supports and whose magnitudes it does not.
Rounds 1 and 2 named the same weakness, so it belongs to a fixture with no numbers in it rather than
to any wording. This reading is the record's, taken from the reports; it is not one of the scored
measures, and no measure covers it.

### Incidental, not measured

Before the fixture was restored, two runs found the source file absent and declined rather than
inventing a subject, each citing Phase 1's decline clause. Both then observed that the skill does
not say whether the four-form requirement applies to a declined report, and each said the reading
that decline terminates before Phase 4 was its own rather than the skill's. That is a gap in the
skill, found while running this scenario and not by it; it is recorded here so it is not lost, and
it is not among this record's measures.

## What this does not show

- **Two reps per arm, and no variance measure.** Enough to show the conflict is reported as settled
  where it was not before; not enough for a rate, and below what the cited protocol asks.
- **Round 1 had no `scoring.md`.** Its measures were fixed after its results were read, and two rows
  had to be re-derived above. `scoring.md` fixes them for the next round.
- **The ratio row fix is unmeasured.** Arm B rep 2 still named `Tables, lists, or callouts outnumber
  prose lines` as a conflict it had to judge itself, and that row was scoped afterwards in a separate
  commit. No arm ran against the scoped row.
- **Every arm read `SKILL.md` alone.** The skill directs Phase 4 to `references/readability.md` and
  Phases 1 and 3 to `references/edge-cases.md`, and no arm in any round was given them. Every result
  here measures the skill body without its references. The limitation is constant across arms, so it
  does not confound a comparison between them, and it does bound what any of them says about the
  skill as installed.
- **One fixture, one subject domain.** A numerical or architectural subject was not run, because the
  mandate is not under pressure there.
- **Round 1 found a weakness this scenario did not measure.** Arm A rep 2 reported that "Plan all
  four forms" is weaker than "include". No arm's repair addressed it at the time; a later round's
  review reported it independently, the sentence now states an output obligation, and round 3
  measured the replacement. Kept because it records what round 1 saw, and corrected because a
  limitation is a claim about the present.
