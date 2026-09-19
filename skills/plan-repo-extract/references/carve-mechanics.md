# Carve Mechanics

The non-obvious detail behind Phase 3-4 for a GO verdict. The dispositions
(sever/invert/duplicate/pull-along) and the ordered step sequence already live in SKILL.md Phase 3-4;
this file only adds what those do not say. Ecosystem-neutral.

## Dependency inversion — the failure mode to watch

After every outbound edge is dispositioned, the boundary must be one-way. Any residual back-edge is a
**cross-repo cycle** — worse than an intra-repo one, because the two repos now version-lock: neither
can release without the other. If no clean disposition exists for an edge, that is a signal to
revisit the boundary (or the verdict), not to accept the cycle.

## Target blueprint — why reconcile rather than reverse-read

Extract toward the boundary you *would design*, not merely the one that grew. A pure reverse-read of
the existing seam freezes an accidental boundary into a public API that can no longer change freely.
Reconciling the forward-designed blueprint against the recovered seam turns each divergence into a
deliberate choice — fix it during the carve, or accept it as declared debt — so the carve is a
decision rather than a snapshot.

## Public API hardening

The internal surface the parent used becomes the public API; everything else stays private. Do not
blindly promote leaked `internal`/`pub(crate)` items — reconsider whether each truly belongs in the
surface. Once public and versioned it can no longer change freely, so state the semver /
compatibility commitment up front, not after the first external consumer pins it.

## History strategy

Preserve (`git subtree split`, `git filter-repo`) versus fresh start is covered in SKILL; the
non-obvious part is that path/rename filtering is **fiddly**. A rename in the component's past can
silently drop history when the filter path misses the old location, so the plan should name the exact
paths to carry and the expected history shape, and defer the command itself to execution.

## Consumer migration and its standing cost

The non-obvious cost is ongoing, not at cut-over: **cross-repo version coordination** — the diamond /
lockstep-bump problem, where every component change now needs a release plus a matching consumer
bump, forever. Weigh this in the Cost axis, not just in the migration steps. At cut-over, a
path/local dependency waypoint (still one working tree) is far less risky than a big-bang publish-cut.

## New-repo scaffolding

SKILL lists what must exist (manifest, build, CI, license, versioning). The non-obvious constraint:
the extracted repo must build and test with **no implicit reliance on the parent's toolchain** —
shared lint config, root-level scripts, or CI steps the component silently inherited must be made
explicit in the new repo, or the first standalone build breaks.

## Why an in-repo package waypoint

Making the component a workspace member *before* moving it to a new repo lets you invert dependencies
and cut consumers over while still in one working tree — cheap to verify, trivial to revert. It turns
one irreversible carve into a series of reversible in-repo moves, retiring most of the risk before the
repo boundary ever exists.
