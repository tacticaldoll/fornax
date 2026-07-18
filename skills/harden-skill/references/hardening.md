# Hardening Reference

Load this when prescribing an instruction form (Phase 3), hardening a discipline rule (Phase 4), or
designing the micro-test (Phase 5). It expands the SKILL.md tables with examples and the reasoning
behind them.

## Match the form to the failure

Before writing or judging any guidance, classify the baseline failure. The form that bulletproofs
one failure type measurably backfires on another — so this classification, not the wording polish,
is what determines whether the guidance binds.

### Discipline violation → prohibition + rationalization table + red flags

The agent knows the rule and skips it anyway when a competing incentive appears (time pressure, sunk
cost, an authority framing, exhaustion). Soft guidance ("prefer", "consider") gives it permission to
negotiate. The binding form is an explicit prohibition, backed by the rationalization toolkit below.

### Wrong-shaped output → positive recipe / contract

The agent *does* the thing, but the output is the wrong shape: the verdict is buried under
throat-clearing, the dispatch prompt is bloated, the input is restated instead of acted on. The
binding form states what the output **is** — its parts, in order — leaving nothing to negotiate.

Prohibitions backfire here. Under a competing incentive ("make the prompt self-contained"), an agent
told "don't restate the spec" produces *more* of the unwanted content, not less — in head-to-head
wording tests the prohibition arm trended worse than even a no-guidance control. A recipe has no
such opening: the output either matches the stated shape or it does not.

```markdown
# ❌ Prohibition on a shape problem — backfires
Do NOT restate the requirements. Do NOT narrate your process.

# ✅ Recipe — states the shape
Output, in order: (1) the verdict (pass/fail) on line one; (2) up to three findings, each one
sentence; (3) the single next action. Nothing before the verdict.
```

### Omitted element → structural REQUIRED slot

The agent produces an artifact but drops a part of it. Prose reminders near the template are read as
optional. The binding form is a REQUIRED field or slot in the very template the agent fills in, so
the omission is visible as a blank.

### Condition-dependent → conditional on an observable predicate

The right behavior depends on context. An unconditional rule plus exemptions ("X, unless…") invites
the agent to decide it is exempt. Key the behavior to a predicate the agent can *observe*: "if a
working brief already exists in the session, reference it instead of re-deriving it."

## Rules for whichever form you pick

- **No nuance clauses.** Appending "…unless it matters" to a winning recipe degraded it from
  consistent to noisy in wording tests. A real exception is its own conditional on an observable
  predicate, not a trailing hedge.
- **Exemption clauses do not scope.** "This limit doesn't apply to code blocks" still suppresses code
  blocks. If part of the output must be exempt, restructure so the rule cannot reach it.
- **One binding example beats three weak ones.** Show the before/after in the single most relevant
  form; do not dilute across many variants.

## Rationalization toolkit (discipline rules only)

Agents are capable and will find loopholes under pressure. For discipline rules, add these on top of
the prohibition. Do **not** apply them to shape or omission failures.

### Close every loophole explicitly

Do not just state the rule — forbid the specific workarounds the baseline surfaced.

```markdown
# ❌ Leaves room to negotiate
Write code before the test? Delete it.

# ✅ Closes the loopholes
Write code before the test? Delete it. Start over.
No exceptions: don't keep it as "reference", don't "adapt" it while writing the test, don't look at
it. Delete means delete.
```

### Address spirit-vs-letter up front

A single early line cuts off an entire class of rationalization:

```markdown
**Violating the letter of the rule is violating the spirit of the rule.**
```

### Build the rationalization table from the baseline

Every excuse the agent produced in the no-guidance run goes in the table, paired with its rebuttal.
This is why the baseline must be captured verbatim.

| Excuse | Reality |
|---|---|
| "Too simple to bother." | Simple cases break too. The check costs seconds. |
| "I'll do it afterward." | Afterward never has the same information or incentive. |
| "I'm following the spirit, not the ritual." | The ritual is how the spirit is enforced. |

### Create a red-flags self-check

Give the agent phrases that signal it is mid-rationalization, so it can catch itself:

```markdown
## Red flags — STOP
- "I already checked this manually."
- "This case is different because…"
- "It's about the spirit, not the letter."
All of these mean: stop and follow the rule.
```

## Micro-test protocol

Micro-tests verify the *wording*; they are fast enough to iterate on and precede the slow pressure
scenarios. They do not replace pressure scenarios for discipline skills.

1. **One fresh-context sample per call.** A raw API call, or a single-shot subagent where no API
   access exists. System prompt = the realistic context the guidance will live in (the full skill or
   template, not the clause in isolation). User message = a task that tempts the failure.
2. **Always include a no-guidance control.** If the control does not exhibit the failure, there is
   nothing to fix — stop and drop the guidance.
3. **5+ reps per variant.** Single samples lie.
4. **Read every flagged match by hand.** Score programmatically if you like, but template echoes and
   quoted counter-examples masquerade as hits and inflate both failure and success counts.
5. **Treat variance as a metric.** When guidance lands, reps converge on the same shape. Five
   different interpretations across five reps means the wording is not binding yet — tighten the form
   before adding words.

## Pressure scenarios (discipline skills, final gate)

After micro-tests pass, run the discipline rule against combined pressures — time + sunk cost +
authority + exhaustion in one scenario — because rules that hold under a single pressure often fold
under two. Capture any new rationalization the agent invents, add its counter, and re-test until the
rule holds. Where the host lacks subagent tooling, hand this protocol to the user rather than
folding an execution dependency into the target skill.
