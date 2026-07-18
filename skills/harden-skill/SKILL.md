---
name: harden-skill
description: Use when an agent needs to harden a skill's instructions so they reliably change agent behavior; diagnoses each intended behavior's baseline failure, matches it to the right instruction form, hardens discipline rules against rationalization, and specifies a micro-test protocol rather than editing the skill or running the tests itself.
---

# Harden a skill
Use this skill to make a skill's *wording* bind. Authoring a skill is only half done when the prose
reads well; the other half is whether an agent under load actually does what the prose intends.
This skill finds where the guidance will fail under pressure or be rationalized away, and
prescribes the instruction form that holds.

Governing intuition: **you cannot harden a behavior you have not named, and you should not add
guidance for a failure you have not seen.** State the behavior each passage is trying to produce,
the failure an agent falls into without it, and match the form to that failure — do not reach for a
prohibition by reflex.

It produces a hardening plan: per-behavior verdicts, recommended rewrites, and a verification protocol
the agent (or user) then applies as a separate act.

**Input**: the skill instructions under authoring or revision — a `SKILL.md` (draft or existing), a specific rule or section, or a proposed wording change; if none is given, ask which skill or passage to harden.

**Boundary**: diagnoses and prescribes only — produces a hardening plan; does not edit the target skill or run the tests.

## Workflow

### Phase 1: Inventory the intended behaviors

Walk the target prose and, for each passage of guidance, write one line: *what agent behavior is
this trying to produce?* Guidance that maps to no concrete behavior is decoration — flag it. A
passage may carry several behaviors; split them, because different behaviors may need different forms.

### Phase 2: Classify each baseline failure

For each behavior, name what an agent naturally does **without** this guidance — the baseline
failure. This is the crux: the form that bulletproofs one failure type backfires on another. Sort
each into one type:

| Failure type | Signature |
|---|---|
| **Discipline violation** | Agent knows the rule and skips it under pressure (time, sunk cost, authority, exhaustion) |
| **Wrong-shaped output** | Agent complies, but the output has the wrong shape (buried verdict, bloated prompt, restated input) |
| **Omitted element** | Agent leaves out a required part of something it already produces |
| **Condition-dependent** | The correct behavior depends on a predicate the agent must first observe |

If you cannot state a plausible baseline failure for a behavior, that behavior may need **no**
guidance at all — say so rather than inventing a rule.

### Phase 3: Match the form to the failure

Prescribe the form that fits each failure type, and flag any current wording whose form is
mismatched (it will backfire, not just underperform). Load
[references/hardening.md](references/hardening.md) for the full table with examples and the evidence
behind it.

| Baseline failure | Right form | Backfiring form |
|---|---|---|
| Discipline violation | Prohibition + rationalization table + red-flags list | Soft guidance ("prefer…", "consider…") |
| Wrong-shaped output | Positive recipe / contract: name the output's parts, in order | Prohibition list ("don't restate", "never narrate") |
| Omitted element | Structural REQUIRED slot in the template they fill in | Prose reminder near the template |
| Condition-dependent | Conditional keyed to an observable predicate | Unconditional rule + exemption clauses |

### Phase 4: Harden discipline rules against rationalization

**Only for discipline-violation behaviors.** For each, load the toolkit in
[references/hardening.md](references/hardening.md) and produce: the specific loopholes to close
explicitly, a rationalization table (excuse → reality) drawn from the baseline, a red-flags
self-check list, and a spirit-vs-letter clause. Do **not** apply this prohibition toolkit to
shape or omission failures — there it measurably backfires.

### Phase 5: Specify the verification

No rewrite ships on faith. Specify a micro-test for the changed wording:

- **Fresh-context samples** — system prompt = the realistic context the guidance lives in (the full
  skill, not the clause alone); user message = a task that tempts the failure.
- **A no-guidance control is mandatory.** If the control does not exhibit the failure, there is
  nothing to fix — drop the guidance.
- **5+ reps per variant**; single samples lie. Read every flagged match by hand (template echoes and
  quoted counter-examples masquerade as hits).
- **Variance is a metric** — five different interpretations across five reps means the wording is not
  binding yet.

For discipline skills, full pressure scenarios (combined time + sunk-cost + authority) are the final
gate after micro-tests pass. This protocol is executed as a separate step after the hardening plan
ships — where the host has subagent tools the agent can run it then; otherwise hand it to the user.
Keep this dependency out of the target skill's core workflow.

## Output Format

```markdown
# Hardening Plan — [skill or passage]

**Scope**: [what was hardened]

| Intended behavior | Baseline failure | Failure type | Current form | Verdict | Prescribed form |
|---|---|---|---|---|---|
| … | … | discipline / shape / omission / conditional | … | binds / will backfire / untested | … |

## Recommended rewrites (not applied)
- [behavior] → concrete wording in the prescribed form.

## Discipline hardening (discipline rules only)
- Loopholes to close · rationalization-table entries · red-flags list · spirit-vs-letter clause.

## Verification protocol
- Micro-test spec (system prompt, tempting task, no-guidance control, 5+ reps).
- Pressure scenarios — discipline skills only.

## Open assumptions
- [Behaviors whose baseline failure was assumed rather than observed.]
```

## Rules

- Read-only. Recommend wording and tests; do not edit the target skill or run the tests as part of
  this skill — the agent applies them as a separate, explicit step.
- Name a baseline failure for every behavior. A behavior with no plausible failure needs no
  guidance; put it under open assumptions, do not manufacture a rule.
- Do not reach for a prohibition by default. Prohibitions bind discipline failures and backfire on
  shape and omission failures.
- No nuance clauses, no exemption clauses. "Don't X unless it matters" and "this doesn't apply to Y"
  both reopen the negotiation — express a real exception as its own conditional on an observable
  predicate, or restructure so the rule cannot reach the exempt part.
- Every micro-test includes a no-guidance control; guidance that beats nothing is the only guidance
  worth keeping.
- Stay in lane. To decide whether a skill should exist or what shape it takes at all, point to
  `scope-new-skill`; to test whether governance prose should become enforcement elsewhere, point to
  `audit-governance`. Structural and mechanical checks (frontmatter, links, naming) are covered by
  `scripts/validate_skills.py`, not by this skill — hardening is about whether the wording binds.
