# Evaluation dimensions

Six evaluation dimensions plus a decision, with ready/concern signals. Each
dimension states a **language-neutral principle first**; Rust appears only as a
marked illustration ("e.g. in Rust, …") — translate it to your ecosystem's
equivalent. Run them in order; stop early when a dimension yields a decision. Each
finding must be grounded in the candidate repo (grep results, file citations,
governance lines), never in the dependency's own claims.

## 1. Pain existence

Does the problem the dependency solves empirically exist here?

| Ready (continue) | Concern (lean decline) |
|---|---|
| You can point to the duplication, boilerplate, or missing guarantee in the repo | The pain is described by the dependency's docs but not found by grep |
| The need recurs across multiple sites | A shared module everyone already imports solves it (e.g. in Rust a `*-core` crate) and consumers use it without re-implementing |

Technique: grep for the thing the dependency would replace before reading its API.
"Abstraction is not the remedy for duplication that isn't there."

## 2. Mechanism vs. load-bearing property

Does the dependency's core mechanism contradict a property this codebase depends on?

First name the project's **load-bearing properties** — the invariants that, if
broken, break the design. Find them by reading the central types/interfaces and the
composition root, not by assumption. Common families (with a language-specific
instance for each):

- **Composition / substitutability model** — how implementations are swapped and
  wrapped (interface + decorator, dependency injection). A mechanism that forces a
  different composition style fights this. (e.g. in Rust, deps held behind
  `Arc<dyn Trait>` and wrapped for cache/retry/logging; a mechanism needing
  generics-over-context on those traits breaks object-safety.)
- **Concurrency / runtime model** — the project's chosen event loop, executor, or
  threading model; a dependency hard-wired to a different one conflicts. (e.g. in
  Rust, a crate tied to a specific async executor.)
- **Constrained execution environment** — a platform limit the code respects: no
  runtime/allocator, sandboxed, size-bounded. A dependency that pulls the excluded
  surface conflicts. (e.g. in Rust, a `no_std` crate whose transitive tree requires
  `std`/an allocator.)
- **Determinism / replay** — a dependency introducing hidden I/O, clocks,
  randomness, threads, or global state on a path that must be reproducible.
- **Error / failure model** — the project's failure discipline (exceptions vs.
  returned error values vs. typed error results); a dependency forcing the opposite
  at the boundary.
- **Memory / ownership model** — the resource and lifetime discipline the code
  relies on. (e.g. in Rust, a dependency demanding lifetimes/borrows the code avoids.)

| Ready | Concern |
|---|---|
| Mechanism composes with the load-bearing properties | Mechanism contradicts one of them |
| Conflicts are confined to an opt-in edge | The conflict sits on the hot/core path |

A mechanism that fights a load-bearing property is usually disqualifying regardless
of ergonomics. See `example-lenses.md` for worked conflicts.

## 3. Boundary feasibility

Even if wanted, can you apply it given what you own?

| Ready | Concern |
|---|---|
| You own the types/interfaces you'd need to extend or implement the dependency's contract on | You cannot legally attach the dependency's contract to the types you have (e.g. in Rust the orphan rule blocks `impl ForeignTrait for ForeignType`; elsewhere, sealed/final classes or a no-monkey-patching policy) |
| The substrate is yours to change | A frozen/vendored substrate (submodule, pinned/vendored dep) may not be edited |
| License + supply-chain gate pass | New/unvetted license, unknown registry/source, or an unpinned/wildcard version (e.g. in Rust, `deny.toml`, registry/source policy) |

## 4. Governance placement

Where does adoption land in the project's stated priorities?

- Read `PROJECT.md`, `AGENTS.md`, `CONTRIBUTING`, ADRs, or governance docs. If a
  change-prioritization order exists, map the adoption onto it.
- If none exists, infer the spirit from README/architecture and say you inferred it.

| Ready | Concern |
|---|---|
| Protects the core contract or strengthens the spine | Only adds ergonomics or integration scope (lower tier → higher bar) |
| Fits a declared, current priority | Contradicts a settled design stance (e.g. "no declarative DAG", "stay in our lane") |

## 5. Cost, maturity, reversibility, idiom-retreat tell

| Ready | Concern |
|---|---|
| Shipped and proven — released, used by ≥1 real codebase | Pre-1.0, unreleased, or roadmap-only — vaporware you cannot build, run, or adopt |
| Small dependency-tree delta; permissive license; fast build | Heavy transitive tree or a costly build step (e.g. in Rust, proc-macros pulling `syn`/`quote`/`proc-macro2`) |
| Low exit cost; localized blast radius | Pervasive API surface; hard to back out; lock-in |
| Compatible with the project's minimum-toolchain / language-version floor | Raises the minimum supported toolchain or forces a version bump (e.g. in Rust, MSRV or an edition bump) |

Maturity gates the rest: if the candidate is not shipped, the other cost signals
are moot — you are evaluating a roadmap, not a dependency. Lean **defer** until it
ships, naming "ships and is proven on another codebase" as the trigger.

**Idiom-retreat tell:** inspect the dependency's *advanced* tier (its escape
hatches, "for hard cases use…"). If it quietly converges back to what you already do
by hand — its "hard" path collapses into your existing idiom — the abstraction is
thin: it adds vocabulary over where the language already pushes you. Strong signal to
decline or adopt only narrowly. See `example-lenses.md` Lens A for a worked instance.

## 6. Earn the abstraction (N≥2)

If adoption implies extracting a **shared** layer across consumers:

| Ready | Concern |
|---|---|
| Two or more real consumers with observed, concrete overlap | One consumer plus a hypothetical second |
| Extract the demonstrated overlap | Pre-abstracting the predicted shape from N=1 |

From a single consumer you build the wrong shape — wait for a second real consumer
before extracting. With one consumer, scope to this repo only. If the shared layer
would touch a frozen substrate, it must live in a **new consumer-side module** the
substrate does not depend on — never by editing the substrate.

## Decision

The four terminal decisions and their drivers (Adopt / Adopt narrowly / Defer /
Decline) are defined in the Workflow's Decision step in [SKILL.md](../SKILL.md).
Name the dimension(s) that drove the verdict.
