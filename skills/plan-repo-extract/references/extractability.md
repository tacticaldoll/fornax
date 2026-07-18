# Extractability Assessment

The go/no-go judgment behind Phase 2 — whether a cohesive component should become its own repository.
The default answer is **no**: a separate repo is a standing cost, and it must be earned. Load this
when scoring a candidate. Language- and ecosystem-neutral; "package"/"publish"/"repo" mean whatever
your ecosystem uses.

## The four axes

### 1. Cohesion — is it one thing?

- **Strong**: a nameable single responsibility with a natural public surface; a reader can state what
  it is in one sentence without "and".
- **Weak**: a grab-bag, an arbitrary slice ("everything under `utils/`"), or a layer that only makes
  sense embedded in the parent's flow.

If cohesion is weak, stop — there is nothing clean to separate out. (Consider `plan-split` to *create*
cohesion internally first, then reassess.)

### 2. Coupling severability — can the umbilical be cut?

Map the component's **outbound** dependencies on the rest of the repo. For each, is there a
disposition that leaves the component depending only outward/downward and on external packages?

- **Severable**: the edge can be removed (dead/incidental), inverted (parent depends on the
  component, not vice versa), satisfied by a small duplicated primitive, or pulled along (the
  dependency genuinely belongs to the component).
- **Not severable**: the component reaches deep into parent internals — shared mutable state, a
  central type it cannot own, a framework the parent controls — with no clean inversion.

A component that cannot end up **acyclic-independent** (no dependency back on the parent) is not
extractable, period. Independence is the bar, not a nice-to-have.

### 3. Independent value — does it want to stand alone?

- **High**: a real or likely **second consumer**; a distinct release cadence from the parent; a
  domain that is genuinely reusable (a protocol, a format, a client, an algorithm).
- **Low**: only ever consumed by this one parent, released in lockstep, with no reuse on the horizon.

Low independent value is the most common reason a *technically* extractable component should still
stay in-repo. Extraction without a second consumer is often infrastructure ahead of a forcing
function — prefer **DEFER** (born when a second consumer appears) over a speculative split.

### 4. Cost — is it worth it?

Weigh the standing costs a separate repo incurs:

- A hardened, versioned **public API** (former internals can no longer change freely).
- **Split history** work (subtree/filter-repo) or lost provenance.
- Its **own build, CI, release, and dependency** maintenance.
- **Consumer migration** and ongoing cross-repo version coordination (the diamond/lockstep-bump
  problem).

## Verdict

| Verdict | When |
|---|---|
| **GO** | Cohesive, severable to acyclic-independence, real independent value, and benefit exceeds cost |
| **DEFER** | Cohesive and severable, but no forcing function yet (no second consumer / no distinct cadence) — born when built |
| **NO** | Weak cohesion, non-severable coupling, or cost dwarfs benefit — keep in-repo; optionally `plan-split` internally for the single-responsibility win without the repo cost |

State the verdict with one line per axis, so the reader sees *why*, not just the call. A well-argued
NO or DEFER is as valuable as a GO — it prevents a costly, hard-to-reverse split.
