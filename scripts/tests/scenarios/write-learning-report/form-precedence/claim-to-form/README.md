# Claim-to-form selection — behavioral micro-test

## Protocol — 2026-09-18

This scenario tests conditional form selection and semantic grounding, replacing the former
presence-only obligation. It is maintainer evidence, not part of the installed skill package.
Scoring was fixed in [scoring.md](scoring.md) before samples were requested.

Variants: no-guidance control with structured-form obligations removed; unchanged baseline skill;
preflight-only with claim-to-form selection added but the old obligations retained; full candidate
with selection, obligations, quality checks, attack, and readability reference aligned. The
unchanged baseline is the no-guidance variant; all variants retain unrelated source-fidelity and
report structure instructions. Full snapshots and references must be retained with any future results.

Fixtures: [qualitative](fixtures/qualitative.md), [structural](fixtures/structural.md), and
[numerical](fixtures/numerical.md). Each variant receives five fresh-context samples per fixture.
The qualitative case has substantive experience but no operational judgment criterion; the other
cases specify inspectable rules. Read all output, including the report and handover, by hand.

Prompt: use the supplied complete skill and its references to turn the supplied notes into a
self-contained learning report in Traditional Chinese. Produce the report and the handover the
skill calls for. Use only this material; do not browse, run models, or write files. No evaluator
conclusions, expected forms, or scoring rules are supplied to the generating model.

The complete skill, both references, and fixture are supplied together as task context. Each CLI
invocation starts a new ephemeral session in an isolated temporary directory. Unlike a raw API
system-prompt experiment, skill instructions are supplied in the user task as they are on normal
manual invocation. This host-specific sampling setup is not a dependency of the shipped skill.

## Execution status — 2026-09-18

Not executed. Automatic approval review rejected the attempted launch of fresh Codex CLI sessions
because sending the skill and fixtures to the configured external model service was not explicitly
authorized. No sample report or score was produced. This document specifies a future experiment;
it is not evidence that the candidate changes behavior. Existing evidence entries account for the
parent scenario directory, not for a measured result of this proposal.

Before execution, freeze full variant snapshots and references and identify the model destination.
Request authorization for the payload transfer. After execution, retain full reports and metadata,
score them against the prewritten rubric, and register evidence for the exact candidate measured.
A subsequent wording repair needs a new treatment run or a superseded evidence entry.
