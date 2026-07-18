# Boundary Reference

Load this in Phase 3 to pressure-test a component partition. These are heuristics for *where* a
boundary belongs and *when* not to draw one — not a fixed architecture.

## Draw boundaries along variation, not nouns

The most durable boundary hides something that is likely to change behind a stable interface
(information hiding). Ask of each candidate component: *what does it let the rest of the system
ignore?* A component that hides a volatile decision (a storage engine, a wire format, a provider, a
policy) earns its interface. A component drawn around a data noun (`User`, `Order`) with no hidden
variation is usually just a table with methods — a weaker boundary.

- **What varies independently → its own component**, behind an interface the rest depends on.
- **What is stable and shared → a primitive** many components may depend on.
- **What varies together → one component**; splitting it spreads one change across many edits.

## Cohesion: one reason to change

A component should have a single reason to change. Signals it does not:

- Its name needs "and" (`parsing and validation and reporting`).
- Two unrelated consumers pull it in opposite directions.
- A typical change touches only part of it, repeatedly — that part wants to be its own component.

Conversely, two components that **always** appear in the same change are one responsibility split
prematurely — merge them.

## Coupling and dependency direction

- **Point dependencies at stability.** Depend on things less likely to change than you are —
  abstractions and stable primitives, not volatile peers.
- **Acyclic, always.** If A needs B and B needs A, you have one component pretending to be two, or a
  missing third that both depend on. Invert one edge (introduce an interface the depender owns) or
  merge.
- **Depth over breadth of coupling.** Many components each touching one narrow interface is healthier
  than a few that reach into each other's internals.

## Interface minimalism

Expose the narrowest surface that serves real consumers. Every public name is a promise you must keep
and a thing others can couple to. Keep constructors, helpers, and intermediate types internal.
Design the interface from the *consumer's* need, not from what the implementation happens to have.

## When NOT to decompose

Decomposition has a cost: indirection, more interfaces to keep honest, more places to look. Do not
pay it without a return.

- **No second consumer yet.** An abstraction extracted for one caller is shaped by a sample of one
  and usually wrong. Wait for a real second consumer before generalizing (echoes `assess-dependency`'s
  earn-the-abstraction bar).
- **The split would not follow a real seam.** If every change still crosses the boundary, the
  boundary is in the wrong place — or should not exist.
- **A cohesive core.** The part that *is* the feature's purpose should stay whole; fragmenting it
  raises analysis cost without buying independence.

## Optional lenses (apply only if one fits — do not force a paradigm)

- **Ports & adapters** — when the volatile things are *external* (DB, transport, third parties):
  define a port (interface) the core owns; each external integration is an adapter behind it.
- **Layering by dependency, not by folder** — a layer is meaningful only if dependencies cross it in
  one direction; layers that call back upward are not layers.
- **Pipeline / stages** — when the work is a transformation sequence, each stage is a component with
  a typed input/output; stages compose without knowing each other.

These are lenses for *recognizing* a boundary that already fits the forces, not templates to impose.
When none fits cleanly, the force-and-cohesion heuristics above decide.
