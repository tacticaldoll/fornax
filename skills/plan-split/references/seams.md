# Seam Analysis

Detailed patterns for finding decomposition seams and judging each extraction. Load this when the
seams are non-obvious or the dependency graph is tangled. Language-neutral; "module" means whatever
unit your language extracts into (file, package, class, namespace), and "re-export" means whatever
mechanism forwards a name so its public path is preserved.

## Seam shapes

- **Contiguous cluster** — a coherent responsibility occupying one span (e.g. one builder family, one
  parsing layer). The cleanest split: lift the span into a module, leave a re-export.
- **Scattered cluster** — one responsibility spread through the unit, interleaved with others (e.g. a
  set of helpers each sitting next to a different caller). Real, but higher-churn: collect the
  scattered members into one module and repoint. Verify you gathered *all* of them.
- **Shared primitive** — a helper several clusters call. It decides where the seam falls: it belongs
  with the layer it most cohesively serves, and the other callers reach it across the new boundary.
  A primitive used by *every* cluster is usually a leaf module of its own.
- **Layer stack** — the unit is really N layers stacked (e.g. lexing → parsing → graph-walking). Each
  layer is a seam; extract from the bottom (leaf) up.

## Dependency direction and cycles

The single most important analysis: after the cut, which way do the edges point?

- **One-way (good):** the extracted piece depends on lower layers only; the parent depends on the
  piece. No back-edge.
- **Back-edge (smell):** the extracted piece reaches *back up* into the parent for something. Even
  where the language permits an intra-unit cycle, it signals the seam is in the wrong place. Usual
  fix: move the reached-back item *down* into the extracted piece (or into a shared leaf), so the
  edge points one way.
- **Mutual (worst):** two pieces reference each other. Find the shared kernel and extract *it* as a
  leaf both depend on.

When an extraction would create a cycle, prefer to **change the seam** over accepting the cycle.

## Contract preservation

Behaviour-preserving means the observable surface is byte-for-byte reachable as before.

- **Re-export facade:** when moving a publicly-reachable symbol into a submodule, forward it from the
  original location so every existing path still resolves. The mechanism is language-specific (a
  re-export, a public alias, a glob forward); the plan names *that a facade is needed*, not the
  syntax.
- **Naming collision:** a new module can collide with an existing name in the same namespace. Prefer
  a directory/sub-namespace that mirrors an existing sibling structure over a suffix hack, so the new
  names read symmetrically with what is already there.
- **Doc / reference repointing:** moving a symbol can strand references to it — in-doc links, comments
  that name it, and *tooling that only checks some surfaces* (e.g. a doc-link check that skips
  private items). Plan to repoint these, and note that a standard gate may not catch a stranded
  private-surface reference.

## Minimal visibility

Plan the narrowest visibility each moved item can take and still be reached:

- Used only inside its new module → **private**.
- Used only by the parent that owns the module → **parent-restricted** (whatever your language calls
  "visible to the enclosing scope only").
- Used across sibling modules → **package/crate-internal**.
- Part of the public contract → **public** (unchanged).

Widening "just in case" leaks surface and invites drift. A frequent review finding is an item left
one level too visible after a move — plan the tight level up front.

## What is artificial (keep it whole)

Not everything large should be split. Keep a cluster whole when:

- It is the **cohesive core** that *is* the unit's reason to exist (splitting it scatters one
  responsibility across files and raises analysis cost instead of lowering it).
- The members only make sense **together** (they share private state, or a tight mutual invariant).
- The split would force a **shared primitive to duplicate** or open a cycle.
- The "seam" tracks a **naming coincidence**, not a real responsibility boundary.

A defensible plan says what it deliberately leaves whole and why, as clearly as what it moves.

## Sequencing

- **Leaf-first:** extract zero-inbound and low-inbound pieces before pieces others depend on, so each
  step compiles and verifies independently.
- **One reason per step:** each extraction is its own reviewable unit; do not bundle unrelated moves.
- **Interlocks:** name steps that must land together (a code split and a dependent test move) and any
  better deferred to a later, separately-justified step.
- **Verification per step:** existing-test parity, type/build check, linter, formatter, and a
  diff-fidelity review that the moved bodies are unchanged except for relocation and visibility. Name
  these as criteria; the exact commands follow the project's conventions.
