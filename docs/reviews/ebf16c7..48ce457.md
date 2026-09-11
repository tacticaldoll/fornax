# Review Record — `ebf16c7..48ce457`

Archived as received, from a review run in fresh context because the author of the range could not
supply one. Kept so the reconciliation in `docs/dispositions/ebf16c7..48ce457.md` can be checked
against its input rather than taken on trust. Transcribed from the message it arrived in, condensed
in its table prose and complete in its findings, verdict, coverage and evidence. Fenced, which
preserves its line citations as text rather than as claims this repository makes.

```text
## Review Record

Source: git diff ebf16c7..HEAD (923c60a, e930f0c, e4fdbdd, 44a1620, 40ff422, 625b9ca, 48ce457;
HEAD 48ce457), against AGENTS.md, PROJECT.md, docs/dispositions/8a45707..2c1b448.md,
docs/reviews/8a45707..2c1b448.md, docs/review-record-contract.md
Calibration: Gates 1-8 (shell_words reads shell command text out of a CI workflow and its result
decides which pins runtime_contract compares — a command/untrusted-input boundary)
Triage: Red 0 / Yellow 4 (read_whole.py, test_module_claims.py, docs/guards.md, the disposition
record) / Green 2 (test_read_whole.py, development-knowns.yaml), both Green files gate-opened anyway
Coverage: partial — gate-reviewed: none, no unit received all eight calibrated gates;
partially-gate-reviewed: read_whole.shell_words (1-6), read_whole.COMMENT (1-6),
test_read_whole.ShellWordTests (1-6), test_read_whole.CommentRule (1-6),
test_read_whole.RequirementsComment (1-6), test_module_claims.test_modules (1-2),
test_module_claims.main_guard (1-2), test_module_claims.entry_point_out_of_place (1-2),
test_module_claims.EntryPointPlacement (1-2), development-knowns.yaml
shell-command-structure-read-by-hand (1, 2, 6), docs/guards.md (Gate 1 only, the ladder closing it
there), docs/dispositions/8a45707..2c1b448.md (Gate 1 only, same); triage-only: none; unread: none.
All six changed paths accounted for.
Findings: 21
Verdict: FAIL at Gate 1 + SECURITY-ALERT + CONTRACT-VIOLATED + CLAIM-REFUTED
Not executed: the CI-only fornax-cli suite (the engine is not installed, confirmed by running it),
the CI-only node check, and no deployment path. Run: the workspace gate, ruff, the unit suite, the
registry verification field's own command, a bash differential over 6,000 constructed commands plus
two hand-built corpora, and every revert each new guards row names, in a throwaway clone at 48ce457
and d0f61da. Working tree unchanged.

Gate Index: 1 fail, 2 fail, 3 pass, 4 pass, 5 pass, 6 fail, 7 blocked, 8 blocked.
Worst-case aggregates. Gate 1 fails for docs/guards.md and the disposition record, closing 2-8 for
those. Gate 2 fails for test_module_claims.py, closing 3-8 for it. Gates 3-5 opened and passed for
read_whole.py and test_read_whole.py; Gate 6 opened for those plus the registry entry and fails for
all three, so no unit reached Gate 7. The security reading is carried by the dual-track alert.

Security Triage Alert
  workflow_pins can still be handed a shorter word list than bash runs, with no Unread, so a pin
  the workflow installs can pass unseen:
      - run: |
          # install the pinned style tool \\
          python -m pip install ruff==9.9.9
  run_commands yields one command — _continued applies the shell's continuation rule to a line bash
  reads as a comment, bash ending a comment at the newline whatever the last character is — whose
  first non-blank character is a hash, so shell_words returns []. workflow_pins reports no pin and
  nothing unreadable; bash -x shows the install running. Not a regression, ebf16c7 answers [] for
  the same text, but it refutes the range's own measured claim that the shortfall class is empty.

Against-Contract (VIOLATED)
 1 two negative controls | the whole-line predicate has only accepted-side spellings and no control
   on the axis where it fails: a text whose accepted prefix continues past a newline.
   shell_words("# c\\necho hi") is [] and no case forbids it | read_whole.py:127
 2 sweep the same class by enumerating the mechanism | enumerating "every place that decides where
   a shell comment ends" reaches runtime_contract._continued and runtime_contract.pins' docstring;
   neither was touched or registered
 3 a reader hands back the whole reading or an Unread | the comment-plus-continuation command, and
   brace and pathname expansion: pip install *.whl gives 3 words against bash's 4, echo a{1,2}b
   gives 2 against 3 | read_whole.py:127
 5 a measurement of the tree must not be written into a commit message | 923c60a says "the workflow
   still yields five commands with none refused"; guards.md states the same fact without it
 8 a superseded claim is marked where it is written | the prospective section for the round this
   range repaired still reads "repaired none", promises five rows while holding two, and its rows
   still read "not measured" | docs/guards.md:418-433
 9 a hand-written grammar's absent owner goes in the registry | 923c60a deleted the evidence item
   recording that install_refs bounds a git-ref and pip-URL grammar by hand. No entry now registers
   it; declined-changes and a guards row still argue from it | development-knowns.yaml:35
Against-Contract (holds): 4 every new guards row reproduces its count under the unit it names,
6 no path:line, 7 a row per accepted finding, 10 no version bump and conventional commits,
11 no false pin reachable through the refusal path, 12 all fourteen repairs are the ones named.

Claims Verified
 1 "the shortfall class is empty" | REFUTED — the comment-plus-continuation command, and expansion
 2 "the residual divergences return more words than bash" | REFUTED — *.whl and a{1,2}b return
   fewer; $HOME, ~, $# return the same count with different content; only $( ), backticks, ${x},
   $(( )) return more
 3 "the measurement now lives under its own dated heading here" | REFUTED — the thirty-three
   against fifty-two reading appears nowhere in guards.md; it survives only in the prior
   disposition and the archived review
 4 the docstring's pointer to that heading | REFUTED — same absence, wrong file named
 5 the prospective section's own text | REFUTED — all fourteen were repaired, two rows remain of
   five, both still read "not measured", and one is for a finding guards.md says has no row
 6 "two commands this could read before are refused; nothing here carries either form" | partial —
   the workflow half verified; the enumeration is short by a third form, a word whose hash is
   quoted: echo "#", echo "### building", echo '#y' z, pip install "#x"==1 all read at ebf16c7 and
   refuse at HEAD
 7 QUOTED-HASH repaired by 1a | partial — the repair is the one named, the matcher and its operator
   branch are gone, and over 6,000 constructed single-line commands there are zero shortfalls and
   zero divergences (2,403 exact, 3,597 refused). The cause is not fully removed: the class reopens
   where the caller hands in text spanning a newline
 8 SHELL-WORDS-CLAIMS-A-REFUSAL closed | partial — the old overclaim is gone and a new one replaced
   it in the same docstring: "a command whose first non-blank character is # is a comment whole" is
   false for any text holding a newline
 9 PROSPECTIVE-SECTION-SPLICED repaired | partial — the named section is gone and the class recurs
   twice in the same range
 Verified: 10 OPERATOR-BRANCH closed, 11 MATCHER-ENUMERATION repaired and the search now surfaces
 the sites it missed, 12 GUARD-DIED repaired, 13 REVERT-INSTRUCTION repaired with both readings
 reproduced, 14 the entry-point pair repaired, 15 the docstring repairs bar the pointer,
 16 CONTROL-MISLABELLED repaired, 17 COMMENTRULE repaired, 18-21 the registry channels, the
 workflow reading, the Reach correction, and the citation gate over 36 documents.
 Claim 1's measurement is also unreproducible as written: "the same constructed set the previous
 rounds used" names no set in this tree.

Structural Causes
 1 Stop joining a continued line whose first non-blank character is a hash, or make shell_words
   refuse text holding a newline instead of answering for the whole of it. The line/text boundary
   has no owner: the caller decides what a command is, the callee assumes it is one line |
   runtime_contract._continued | Gate 5
 2 Change the reading of AGENTS.md, not the code: a hand-written matcher for an uninstallable
   grammar is permitted when the grammar and its absent owner are registered, which this entry
   already does. The prohibition asserted in two durable places was transcribed from the
   disposition's cause statement | the disposition's cause 1 | Gate 6
 3 Re-check the references into a registry entry when an evidence item is deleted; two are orphaned
 4 Have the settling turn delete or re-date the prospective section of the round it just repaired
 5 Point the docstring at the record that actually holds the measurement
 6 Rename the module-level test_-prefixed helper, which is not a test case
 7 Reflow prose after an edit rather than splicing into it

Gate 1: a 102-character prose line in guards.md produced by splicing a symbol name into a sentence;
two consecutive blank lines in the disposition record, the only such run in 31 records.
Gate 2: a module-level def test_modules(root) inside a test module is named as a test case and is
not one — the only module-level test_-prefixed callable in the tree; a pytest-shaped runner would
collect it and error on the missing argument.
Gate 6: 1 the surviving answer is stated for a line and applied to a text; 2 "which AGENTS.md
forbids" misstates the governing document, which permits a hand-written matcher where the owner is
absent and the grammar is registered; 3 the stated cost is short by the quoted-hash form, and the
diagnostic's advice does not apply to it; 4 the comment over COMMENT states two different rules for
one pattern, the newer of which this range's own control refutes; 5 the registry repeats the
misstatement; 6 the deleted evidence item and its two orphaned references; 7 two rewritten cases
assert only the Unread type where the cases they replaced asserted an exact word list, and one
passes for an unrelated reason — it stays green when the hash refusal is deleted.
```
