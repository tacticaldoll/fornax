# Disposition Tests

The detailed judgment behind the four dispositions (dissolve, convert, keep, defer). Load this when
classifying non-obvious claims. The tests are project- and language-neutral; "enforcement" means
whatever mechanism your project uses to make a claim self-checking (tests, CI, types, linters,
schema validation, runtime assertions, a self-check suite, or a generated-and-pinned artifact).

## Test 1 — Structural vs judgment

A claim is **structural** if a mechanism could decide it by reading an artifact, with no appeal to
intent. A claim is a **judgment** if deciding it requires reading why a human chose something.

- Structural: "module A does not depend on module B", "every public function has a doc comment",
  "the config lists exactly these three regions", "type X is serialization-free".
- Judgment: "this layer is a measure, not a tool", "this abstraction earns its complexity", "this
  rejected alternative was worse" — verdicts about meaning, value, or intent.

The stakes are asymmetric. Forcing a **judgment** into a check produces a rule that passes anything
reworded to look compliant — a false-negative engine. When in doubt, classify as judgment and keep
it prose.

## Test 2 — Redundant index vs load-bearing prose

Among structural claims, separate what merely *points at* an enforced fact from what *carries*
something no mechanism holds.

- **Redundant index (dissolves):** a coordinate ("rule 2, 3, 6"), a count ("all N components are
  covered"), a cross-reference number, or a verbatim restatement of an enforced value. These **rot
  on edit** — the enforced source changes and the prose silently drifts. The fix is to delete the
  pointer and let the enforced source (or its generated projection) be the single truth.
- **Load-bearing (keeps):** the *why* (rationale), rejected alternatives, lineage/history, a
  distinction no mechanism encodes (e.g. "the external bound is {X} but the internal allowlist is
  widened to {X, Y} for a structural reason"), or a **stable human-language invariant summary** that
  orients a reader. A one-line invariant summary with near-zero drift and real navigation value is
  NOT an index — keep it.

Rule of thumb: if the sentence would *rot* when the enforced fact changes, it is an index (dissolve). If it
would stay true and keeps carrying reasoning or orientation, it is load-bearing (keep).

## Test 3 — Enforced? Fully enforced? (the coverage trap)

Before calling a structural claim "already enforced", confirm the mechanism covers the **whole**
claim, not one side of it.

- **Direction:** an allowlist / ceiling enforces "at most X" but not "at least X". "Depends on
  **every** dependency it composes" is a lower-bound (completeness) claim an allowlist never checks.
- **Strength:** a text-`contains` or presence check is weaker than a structural fact — a reworded
  clause slips it. That can be acceptable (it still catches the real drift class) but must be
  **stated**, not assumed.
- **Visibility of the check:** a gate may not run over the surface the claim covers (e.g. a doc
  check that skips private items, a lint disabled for generated files). "The suite is green" does
  not prove the claim is enforced where it matters.

A claim that only *looks* enforced is a KEEP or CONVERT, never a DISSOLVE.

## Test 4 — Forcing function (drift-law)

Do not lay down a rule, check, or codified criterion ahead of a real need.

- A CONVERT earns its place when there is a **forcing event**: the prose has actually drifted once, a
  second consumer appeared, or a concrete failure occurred. Absent that, the honest disposition is
  **DEFER** (born-when-built).
- Codifying a positive checklist prematurely does double harm: it is infrastructure no forcing
  function demanded, and it hands future contributors a **target to game** ("tick all five boxes").
  The prior culture of case-by-case refusal often resists violations better than a written test that
  can be reverse-engineered.

## Test 5 — Self-contradiction / over-narrowing

When the challenge proposes a *new* rule or a tightening, check it against the existing charter
before endorsing.

- Does the proposed rule **contradict** a standing decision?
- Does it **narrow** the charter — enforce a stricter invariant than the charter actually holds
  (e.g. reduce "measure OR judgment-neutral mechanism" to "measure only")? Silent narrowing of a
  landed decision is a defect even when the intent is good.

## Anti-patterns

- **Dissolving load-bearing rationale** under a "reduce prose" banner. Removing the *why* to shrink a
  document is a net loss; enforcement proves a fact is *correct*, not that a reader no longer needs
  to *see* it.
- **Judgment disguised as an executable checklist.** If the criterion needs a human to read intent,
  a check is theatre; keep it as a prose rubric for human review.
- **Relocating a hand-maintained index** from prose into a check that hardcodes the same value. That
  moves the rot, it does not remove it. Prefer a check that asserts the *property* (membership,
  absence, a relation), never a frozen literal that must be hand-updated on every legitimate growth.
- **Treating green as proof.** The configured gate may not exercise the claim; name where confidence
  ends.

## Adversarial lenses (Phase 3)

Give each lens a distinct mandate; do not run one reviewer three times.

- **Loophole hunter** — for each CONVERT, construct something that *should* be excluded and try to
  pass the proposed check. A hole means the check is unsound.
- **Consistency auditor** — cite the standing decisions; find any disposition that contradicts one or
  narrows the charter; find any "already enforced" that is only partially covered.
- **Necessity skeptic** — steelman "do nothing": is the forcing function real, is the DISSOLVE
  removing something still needed, is the CONVERT redundant with an existing mechanism?

Converge to the most conservative disposition the evidence supports. It is a successful pass, not a
failed one, when the verdict is "the governance is already well-migrated — change little."
