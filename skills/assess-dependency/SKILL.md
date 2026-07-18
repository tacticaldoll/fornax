---
name: assess-dependency
description: Use when an agent needs to decide whether to adopt a structural dependency into a project; checks local pain, architectural fit, feasibility, and governance, then returns adopt, adopt narrowly, defer, or decline rather than planning implementation.
---

# Assess a dependency
Decide whether a **structural dependency** belongs in this project — a decision grounded in *this*
codebase, not a survey of the dependency's features and not an implementation plan.

Mental model: **run the gates in order and stop at the first that yields a terminal decision**,
rather than running every check to look thorough. The decision, not a survey, is the goal.

Governing intuition: **decline is a valid, common result** — most adoption questions should narrow
or stop before any proposal work begins.

**Input**: the structural dependency under consideration (a library, framework, runtime, or abstraction layer) and the target repo — if the candidate's role is unclear, run the Scope gate first to confirm this skill applies.

**Boundary**: reads and decides only — does not edit files, add the dependency, or run builds; writes only the optional worksheet when asked, and stops at the decision (implementation is downstream).

## Scope gate (Step 0 — do this first)

This skill is for **structural** dependencies: abstraction layers, frameworks,
runtimes, capability/effect systems, DI/contract layers, broker/storage substrates,
serialization frameworks — anything that shapes how code is *written* or
*composed*.

It is **not** for leaf utility libraries (a date parser, a hashing library, a CLI
arg parser). If the candidate is a leaf utility with a local, reversible blast
radius and no architectural mechanism, **stop**: tell the user ordinary judgment
applies (does it work, is it maintained, is the license fine) and that this skill
is overkill. Do not run the full evaluation.

If unsure which it is, ask one question: *"does adopting this change how code is
structured or composed, or is it a self-contained utility called at a few sites?"*

## Workflow

Run the dimensions in order. The order is **blocking**: a dimension that yields a
terminal decision stops the later ones, because they add nothing once the question
is answered. If Dimension 1 shows the pain doesn't exist, or Dimension 2 shows the
mechanism is disqualifying, conclude there — running Dimensions 3–7 to look
thorough only manufactures noise. Record which dimensions were assessed, decided,
or left unreached.

Read [references/dimensions.md](references/dimensions.md) for the full signal
tables; read [references/example-lenses.md](references/example-lenses.md) when you
need a worked mechanism-conflict lens for a known dependency class.

1. **Pain existence — grep before you theorize.** Does the problem this dependency
   solves *empirically exist here*? Confirm the duplication, boilerplate, or missing
   guarantee by search, not by the dependency's marketing; if a shared module already
   solves it, there is no pain to remove — lean *decline*.

2. **Mechanism vs. load-bearing property.** Identify this project's load-bearing
   properties by reading its central types/interfaces and composition root
   (dimensions.md §2 lists the common families). Does the dependency's core mechanism
   *contradict* one of them? A mechanism that fights a load-bearing property is usually
   disqualifying regardless of ergonomics; use a lens from `example-lenses.md` if one fits.

3. **Boundary feasibility.** Even if wanted, *can* you apply it given what you own?
   Check contract attachment to the types you have, frozen/vendored substrates you may
   not edit, license compatibility, and supply-chain gates (dimensions.md §3).

4. **Governance placement.** If the project states a change-prioritization order
   (read `PROJECT.md`, `AGENTS.md`, `CONTRIBUTING`, governance docs), map the
   adoption onto it: does it protect the core contract, strengthen the spine, or
   only add ergonomics/integration? Lower-priority placement raises the bar. If no
   governance doc exists, infer the spirit from the README/architecture and say so.

5. **Cost, maturity, reversibility, and the idiom-retreat tell.** First gate on
   maturity: an unshipped or roadmap-only candidate is vaporware — lean *defer* until
   it ships. Then weigh dep-tree expansion, the toolchain floor, build time, and exit
   cost/lock-in/blast radius against the benefit. Finally check the **idiom-retreat
   tell**: if the dependency's advanced tier collapses back into what you already do by
   hand, the abstraction is thin (dimensions.md §5).

6. **Earn the abstraction (N≥2).** If adoption implies extracting a *shared* layer
   across consumers, require **two or more real consumers with observed overlap**; from
   a single consumer you build the wrong shape, so with one consumer scope to this repo
   only (dimensions.md §6).

7. **Decision.** Conclude with exactly one:
   - **Adopt** — pain exists, mechanism fits, feasible, governance-justified, cost acceptable.
   - **Adopt narrowly** — adopt only the part that fits (often a subset/one "track"),
     scoped to this repo, with the disqualified parts named.
   - **Defer** — revisit when a stated condition holds (N≥2 consumers, the pain
     materializes, a blocker clears). State the trigger.
   - **Decline** — the pain is already solved here, or the mechanism is
     disqualifying. Declining is a successful outcome, not a failure.

## Output

Default: a structured evaluation in chat. Lead with a **Decision** line and a
**Dimension Index** so the verdict and its driver are visible at a glance, then the
per-dimension findings, then a note of what was *not* checked.

```markdown
**Decision**: [Adopt | Adopt narrowly | Defer | Decline] — driven by Dimension [N]

| # | Dimension | Finding |
|---:|---|---|
| 1 | Pain existence | [exists / already solved / —] |
| 2 | Mechanism vs. load-bearing property | [fits / conflicts: <prop> / —] |
| 3 | Boundary feasibility | [feasible / blocked: <reason> / not reached] |
| 4 | Governance placement | [tier / not reached] |
| 5 | Cost, maturity & idiom-retreat tell | [acceptable / concern: unshipped, … / not reached] |
| 6 | Earn the abstraction (N≥2) | [N / n-a / not reached] |

### Findings
[one short paragraph per assessed dimension, grounded with file:line / grep evidence]

### Not checked
[what this evaluation did NOT verify — e.g. did not run the supply-chain gate (in
Rust, `cargo deny`), did not expand the full dependency tree, assessed from the
manifest only, did not build]
```

A dimension left unreached by the blocking order is marked "not reached", not
guessed. If the decision is **Adopt**, the index is the report — do not invent
concerns to pad it. Each other verdict carries a required closing element, stated
in one line after the index:

- **Adopt narrowly** — name the excluded parts and the scope kept.
- **Defer** — state the trigger that would reopen the decision.
- **Decline** — name what already solves the pain, or the disqualifying mechanism.

On request only: write a portable worksheet from
[assets/EVALUATING-template.md](assets/EVALUATING-template.md) (e.g.
`EVALUATING-<dep>.md`) that another repo can run itself.

## Rules

- Read-only unless the user asks for the worksheet artifact. Never add the
  dependency, edit manifests, or run builds as part of the evaluation.
- Ground every finding in *this* repo (cite files, grep results, governance lines),
  not in the dependency's own claims.
- Keep "decline" and "defer" first-class. Do not bias toward adoption.
- **Do not manufacture concerns.** An evaluation skill's failure mode is inventing
  blockers to look thorough, biasing toward decline/defer. If the dependency fits,
  conclude **Adopt** cleanly — silence on a dimension means it raised nothing. State
  every concern with concrete evidence or omit it.
- **State what was not checked.** Name the verifications skipped (builds, supply-chain
  gates, full dep-tree expansion) so the decision's confidence is legible.
- Stop at the decision. Hand an Adopt / Adopt-narrowly verdict off to `plan-implementation` (or a
  proposal workflow); this skill is upstream of both and does not design the implementation.
- Do not run this for leaf utilities (see Scope gate).
