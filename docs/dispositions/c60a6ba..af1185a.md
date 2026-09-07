# Disposition Record — `c60a6ba..af1185a`

**Source**: `docs/reviews/c60a6ba..af1185a.md`, 1 finding, PASS + CONTRACT-VIOLATED
**Scope**: `c60a6ba..af1185a`, whose changed files are three modules under `scripts/`, three test
files, and three records, derived with `git diff --name-only`
**Prior round**: `docs/dispositions/v0.4.1..c60a6ba.md`

The repairs settled here are restatements of two records, landing in the commit that carries this
record; the hash is therefore named nowhere in it, which is what the orphan finding of an earlier
round taught. A later round reads the settlement from this file's own range.

**The finding is against this repository's own record, and it holds.** A round settled a finding
about inventing a record-integrity check, and invented two in the same table while doing it.

## Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | PASS + CONTRACT-VIOLATED | no gate is recorded `fail`, so the gate result is `PASS`, and the two violated contract rows raise the one non-gated flag the verdict carries | pass |
| Calibration / Gate Index | Gates 1–7 | Gates 1–7 each carry a status and Gate 8 is `not inspected`, which is the shape the contract's Gate Index asks for. Recorded as a pass deliberately: reading this as a mismatch is the defect this round settles | pass |
| Finding count | 1 | one Finding row. The two Against-Contract rows key to it — they are the two halves of the same reading, the Gate Index row and the security-alert row of one table — and the input counts them as one finding rather than three, which is the declaration the previous two inputs omitted | pass |
| Coverage | partial, four sets, three modules gate-reviewed at Gates 1–7 and the remainder `triage-only` | the four sets are present; `triage-only` is given as "3 test files and 3 documentation records", which over a fixed delta resolves against `git diff --name-only` and cannot go stale. Read as derived, on the same ground this repository declined `COVERAGE-ENUMERATION-ABSENT` | pass |
| Non-finding sections | not declared | the Responsibility & Dependency Ledger carries three rows, none stating a defect and none counted in the total | not claimed |

## Prior scope resolution

| Prior finding | Scope evidence stated by this round's input | Membership | This round's slot |
|---|---|---|---|
| ABSENT-CLAIM-AS-MISMATCH | the finding and both contract rows report the Record integrity tables of records under `docs/dispositions/`, which are among the changed records this input reads | re-reported | current finding → Dispositions, carried, recurring |
| CHECKER-CANNOT-DECODE | contract row 3 attempts a falsifier against `scripts/check_citations.py`, gate-reviewed at Gates 1–7, and reports it holding | inside | Closed |
| QUOTE-CLOSER-BY-EXISTENCE | contract row 4 attempts a falsifier against `scripts/distribution_manifest.py`, gate-reviewed at Gates 1–7, and reports it holding | inside | Closed |
| EVIDENCE-SECTION-UNBOUNDED | contract row 5 attempts a falsifier against `scripts/evidence_currency.py`, gate-reviewed at Gates 1–7, and reports it holding | inside | Closed |
| FIXTURE-READ-AS-PRODUCT | the input states the fixture findings remain declined | inside | Carried forward, declined — disposition and reason unchanged |
| REVIEW-COVERAGE-AS-FINDING | not re-reported; its unit is a registry outside the changed files | outside | Out of scope this round |
| LIFECYCLE-OMITS-THE-NAMED-PRIOR, GUARDS-LEDGER-MISSES-THE-SETTLING-ROUND, ANCESTRY-STATEMENT-UNBOUND | their units are lifecycle sections, ledger rows and `Verified how` cells of records this input lists as `triage-only` | inside | Carried forward |
| COVERAGE-ENUMERATION-ABSENT, SETTLEMENT-NAMES-AN-ORPHAN, LEDGER-ROW-IN-THE-WRONG-TABLE, DECLINE-NOT-RE-WEIGHED, REACH-STOPS-AT-THE-FILE, PARAGRAPH-SPLIT-NOT-REFLOWED, LEDGER-TABLE-ROUNDS, RAWSCORES-PROVISIONAL | each unit is in a record or file this input lists as `triage-only`, or outside the delta | inside or outside as noted | Carried forward, dispositions and reasons unchanged |
| F-11, F-12 | no record in this tree gives either id a locatable unit | undetermined | Undetermined |

**Three closures, the first this repository has established since the ledger began.** Each meets all
three conditions: the input `gate-reviewed` the module at Gates 1–7, so the relevant gate opened; it
attempted a falsifier against the repaired behaviour and reports it holding, which is the input's
own verification rather than its silence; and nothing elsewhere in the record contradicts the
closure. The twelve dispositions still carried are carried for the same reason as last round — their
units are `triage-only` — and this round is the demonstration that a gate opened over a unit is what
closes a finding, since the three that closed are exactly the three whose units were gate-reviewed.

## Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | The Record integrity table is composed row by row from a reading of the input, with nothing tying its rows to the five checks the contract declares — so a row can be added at will, and the previous repair removed one instance without touching what admits the next | ABSENT-CLAIM-AS-MISMATCH (finding 1, contract rows 1 and 2) | 1a correct the three readings and restate them as passes, saying in each cell what the contract states and that the row had judged on something it does not | restate | `docs/dispositions/74cd7e3..85d0569.md`, the `Calibration / Gate Index` row; `docs/dispositions/v0.4.1..c60a6ba.md`, its `Verdict / Gate Index` and `Calibration / Gate Index` rows and the withdrawn observation in its Recurring section | document — maintainer-owned |
| 1 | " | " | 1b compose the table from the contract's five checks each round, taking the list from `skills/triage-findings/SKILL.md` and answering each — so an invented row has no place to sit rather than being caught after the fact | restate | the authoring step for every future record under `docs/dispositions/` | document — maintainer-owned; taken as the working rule, though nothing verifies it |
| 1 | " | " | 1c derive the check: read each record's Record integrity table and require its row labels to be exactly the contract's five, taking them from the marked template rather than a copy | derive | a new check under `scripts/`, its test, the gate step list, and `README.md`'s generated block | **not taken this round** — see the weighing below |

### Weighing repair 1c against the rule for adding a check

`AGENTS.md` requires naming what a candidate check would have caught and what it costs per change
before adding it.

**What it would have caught** — and this is where the weighing changed, because the number was not
taken from the input. `AGENTS.md` requires sweeping the class rather than rereading the change, so
the sweep was run: take the five checks the contract declares and compare them to the row labels of
every record under `docs/dispositions/`. It reports a sixth row in four records this round's input
never named, and the Result values separate them into two kinds.

Two are the same defect as the finding: `Range already settled` in
`docs/dispositions/v0.4.1..1609403.second-reading.md` and `Triage` in
`docs/dispositions/v0.4.1..e693b19.md`, both scored `mismatch`. Each is an invented row used to
score an input as self-contradictory, which is the finding verbatim.

Two are a lighter thing: `Probe disclosure` in `docs/dispositions/v0.4.1..61789c2.md` and in
`docs/dispositions/v0.4.1..de72982.md`, both scored `pass`. An undeclared row recording an
observation is outside the contract's table but accuses nothing, and the distinction matters for
what a check should refuse.

So the class is not three instances but more, and it was never a first-and-second — the earliest
predates every round that has been reading these records. None reached a user, and two of the
corrected rows did reach `origin/main` in a record that read as settled, one of them carrying an
accusation against a producer that was following the contract.

**What it costs**: the row labels have to come from somewhere. Copied into a script they are a second
list that can disagree with the contract — the exact failure this repository has recorded more than
once. Derived from the marked template in `skills/triage-findings/SKILL.md` they cost a parser for a
table inside a fenced block, which `seam_contract` shows is possible and which nothing currently
needs. The check would also have to admit that a record from before a contract change may carry
different labels, which is the list of places it does not apply that the rule warns about.

**Not taken this round, and the reason is no longer that the class is small.** The sweep removes the
argument this weighing was first written with — a count taken from the input, which is the mistake
the finding itself is about, made once more in the paragraph weighing its repair. What remains is
narrower and holds: `1b` has never been written down anywhere, so no round has yet composed the
table from the contract's list, and the reading that catches this is one command a round can run and
which this round did run. Buying a parser for a fenced table before trying the rule, in the same
turn that discovered the rule was missing, is a check bought instead of a repair attempted.

What replaces the retracted trigger is a condition the sweep can decide: **the next round that finds
a new invented row scored `mismatch` — one written after this record — is the evidence that `1b`
does not bind, and `1c` is then the repair.** The two `mismatch` rows the sweep found are not that
evidence; they predate the rule and are recorded below as standing work rather than as a test of it.
A count of what already existed cannot measure whether a rule written today binds tomorrow.

## Pattern

One cause, and its shape is the one the project memory of this range keeps naming, in its sharpest
form yet: **a rule established in a round lands in that round's own new output, which is the part
nobody re-reads.** Earlier instances were a clause obeyed toward the input and not toward the turn
obeying it, and a self-check answering from its own contents. This one is tighter than either — the
finding being settled was, verbatim, "a record contract row was invented that the contract does not
declare, and an absent claim was then scored against it as a contradiction", and the table settling
it invented two rows and scored a contract-conformant input as contradictory.

What makes this instance useful is that it separates two things the previous rounds ran together.
Removing the offending row was a real repair and it landed; it simply was not a repair of the cause,
because the cause is how the table is composed and the repair was one of its rows. **A repair
confined to the finding's own place is exactly what this skill's governing intuition warns about**,
and this round is the case where the warning was earned rather than quoted.

## Coupling

- `1a` and `1b` are independent: one corrects what is written, the other governs what gets written.
- `1c` is voided by nothing and blocked by `1b` not yet having had a round.

## Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| ABSENT-CLAIM-AS-MISMATCH — a Record integrity table judged a contract-conformant Gate Index and a non-gated security alert as defects of the input, and called the first a repeated defect of the producer | 1 | carried | accept | — |

## Carried forward

Unchanged from the previous round for the same reason — this input lists their units as
`triage-only`, so closure condition 1 is not established — with one exception noted below.

| Finding | Prior disposition | Original reason, unchanged |
|---|---|---|
| LIFECYCLE-OMITS-THE-NAMED-PRIOR | accept | a lifecycle self-check answered `pass` by counting the ids the record had placed rather than by enumerating the prior record's open dispositions |
| GUARDS-LEDGER-MISSES-THE-SETTLING-ROUND | accept | the settling turn reads "the current accepted findings" as the findings its input settled |
| ANCESTRY-STATEMENT-UNBOUND | accept | an ancestry result was written next to a different commit than the one it was measured against |
| FIXTURE-READ-AS-PRODUCT | decline | the reviewed units are a micro-test fixture's deliberate defects, and the security half embeds no value. The input states the decline stands, which is agreement rather than new evidence |
| COVERAGE-ENUMERATION-ABSENT | decline | the coverage line states its derivation, and a set derived from a fixed range cannot go stale |
| SETTLEMENT-NAMES-AN-ORPHAN | accept | a settling commit's hash was read before the commit was final |
| LEDGER-ROW-IN-THE-WRONG-TABLE | accept | the ledger has two row shapes and one was being written wherever its finding's siblings were |
| DECLINE-NOT-RE-WEIGHED | accept | a decline was left standing on evidence the file has since superseded |
| REACH-STOPS-AT-THE-FILE | accept | a Reach cell named a file and stopped |
| PARAGRAPH-SPLIT-NOT-REFLOWED | accept | a repair split an overlong line instead of reflowing the paragraph |
| LEDGER-TABLE-ROUNDS, RAWSCORES-PROVISIONAL | out of scope in earlier rounds | unchanged |

## Closed

| Finding | Prior disposition | Code evidence the cause no longer holds | Input evidence |
|---|---|---|---|
| CHECKER-CANNOT-DECODE | accept | `check_citations.module_symbols` carries a `UnicodeError` branch answering a reason of its own | gate-reviewed at Gates 1–7; contract row 3 attempts the falsifier — a discovered module holding invalid UTF-8 — and reports a diagnostic rather than a crash |
| QUOTE-CLOSER-BY-EXISTENCE | accept | `distribution_manifest.install_refs` takes the first of the opening quote or the word boundary and requires it to be the quote | gate-reviewed at Gates 1–7; contract row 4 attempts the falsifier — a later unrelated quote after an unterminated ref — and reports the nearest-delimiter rule holding |
| EVIDENCE-SECTION-UNBOUNDED | accept | `evidence_currency.load` refuses a second `evidence:` and a missing one | gate-reviewed at Gates 1–7; contract row 5 attempts the falsifier — the section repeated or absent — and reports it holding |

## Out of scope this round

**REVIEW-COVERAGE-AS-FINDING**, declined last round. Its unit is `development-knowns.yaml`, which is
not among this delta's changed files, so this round says nothing about it.

## Undetermined

**F-11 and F-12**, unchanged. The input enumerates its coverage, so this section should be empty for
a record of this kind; these two persist because no record in this tree has ever given them a
locatable unit.

## Recurring

**ABSENT-CLAIM-AS-MISMATCH**, second instance, and the recorded repair's full Reach changed before
it recurred. The prior Reach was the `Range already settled` row of one record; that row was removed
at `c60a6ba` and does not exist. So the repair landed, was complete over its stated Reach, and the
finding came back — which under this skill's own test means the stated cause was wrong, not that the
Reach was short. It is re-derived above as cause 1: not a row to remove, but how the table is
composed.

The previous record's own Recurring section is where this should have been visible. It said `None
among the findings` and then spent a paragraph on a producer defect that did not exist, which is the
same misdirection at one remove — attention on the input's fitness while the record's own new table
carried the finding it was settling.

## Ungrouped

None.

## Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass — answered from the prior record's own tables: `ABSENT-CLAIM-AS-MISMATCH` is re-reported here, three ids are Closed, twelve are Carried forward across eleven rows — the last row carries two ids — one is Out of scope this round, and F-11 / F-12 are Undetermined. Corrected by the `v0.4.1..6ff702e` round: this cell read `eleven`, which counted the table's rows while the check it answers is about ids, and the paragraph above it said twelve |
| Every accepted cause carries at least one repair with an enumerated Reach | pass — cause 1 lists three repairs; `1a`'s Reach names each record and the row inside it, `1b` names the authoring step, and `1c` names the files a check would touch and is not taken |
| Every commit this record names is reachable from HEAD | pass — `c60a6ba` and `af1185a` were checked with `cat-file -e` then `merge-base --is-ancestor` against HEAD. The settling commit is deliberately unnamed: it is the commit carrying this file, and naming it would require reading a hash that does not exist yet |
| Every finding this record accepts has a row in `docs/guards.md` | pass — `ABSENT-CLAIM-AS-MISMATCH` has a row saying nothing can turn red and why, and the three closures keep the guarded rows they already had |
| Every row of this table above the contract's five checks is one the contract declares | pass — the Record integrity table carries exactly the five checks `skills/triage-findings/SKILL.md` declares and no sixth. This row is repair `1b` applied to the record making it, and it is the check the last two records did not run on themselves |

## What this round leaves standing

- **F-11 / F-12**, unchanged.
- **Twelve carried dispositions** whose repairs have landed and which the next round closes if its
  coverage opens a gate over `docs/`. This round proves the mechanism works: the three findings whose
  units were gate-reviewed closed on their input's own falsifiers.
- **Two invented rows scored `mismatch` in records outside this round's coverage**:
  `Range already settled` in `docs/dispositions/v0.4.1..1609403.second-reading.md` and `Triage` in
  `docs/dispositions/v0.4.1..e693b19.md`. Found by the sweep, not by the input, and deliberately not
  repaired here — this skill triages what its input reports, and a defect the review did not reach
  is sent back for review rather than added. They are named so the next round's coverage can include
  them. Two further undeclared rows, both `Probe disclosure` scored `pass`, are the lighter kind: a
  row outside the contract's table that accuses nothing.
- **Repair `1c` unbuilt, with its trigger restated after the sweep retracted the first one.** A new
  invented row scored `mismatch`, written after this record, is the evidence that `1b` does not bind.
- **That the weighing for `1c` first counted only the instances the input named.** The sweep was run
  because `AGENTS.md` requires it, and it found the count wrong — inside the paragraph deciding the
  repair for a finding about taking a reading from the input instead of from the tree. Recorded
  because it is the same shape one level deeper, and the deepest instance this range has produced.
- **That a review found this at all.** The two corrected rows were pushed to `origin/main` in a
  record that read as settled, and the defect was in the part of the round nobody re-reads. What
  surfaced it was another round reading the contract rather than the record.
