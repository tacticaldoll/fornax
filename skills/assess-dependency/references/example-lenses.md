# Example mechanism-conflict lenses

Worked lenses for Dimension 2 (mechanism vs. load-bearing property). Each lens lists
the axes that decide whether a *class* of dependency fits a codebase. Use a lens
when the candidate matches its class; otherwise identify the load-bearing property
directly from the code's central types and interfaces. These are examples, not an
exhaustive set — add lenses as new dependency classes recur. Lens A is worked in
detail (illustrated in Rust); Lenses B–E are one-line reminders of the neutral
principle already tabled in `dimensions.md` §2.

## Lens A — capability / dependency-visibility / DI-contract layers

For crates whose model is "declare required capabilities as bounds on a context
type" (`where C: Has<Logger> + Has<Clock>`), i.e. a port of Haskell's `Has`/`ReaderT`
capability pattern. Score four axes; left = fits the bound-on-context model,
right = does not.

| Axis | Left (fits) | Right (does not fit) |
|---|---|---|
| How consumers get deps | Functions take a context (`fn f<C>(ctx: &C)`); a unifying `C` exists | Deps injected into a struct at construction, stored as fields; no single `C` holds them all — the bound has nothing to bind to |
| `dyn` + decorators | Object-safety not central; generic bounds are fine | Handlers held behind `Arc<dyn Trait>` and decorated; a handler generic over `C` can't become that `dyn` object |
| Who owns the dep types | Yours → you can `impl Has<T>` | Frozen/foreign substrate → orphan rule blocks the impl |
| Async story | Borrowed `&C` across `.await` works | Borrowing `&C` across `.await` hurts, so you already pass `Arc<dyn Trait>` handles — which *is* constructor injection |

Reading: mostly-left codebases can use the **access** half (`Has`/`Provide` + derive),
but keep the bound at the composition root, never on object-safe business traits.
Mostly-right codebases get nothing from the access half; at most a **declaration**
half — metadata *derived from the real injection surface* (constructor fields), with
no generic `C` and no object-safety cost — is viable, and only if the metadata is
derived (never hand-written, which drifts from the real constructor).

This lens is the worked instance of the **idiom-retreat tell** (dimensions.md §5):
the async-story axis above is exactly it — when the dependency's "hard case" guidance
is the plain handle you already pass by hand (here `Arc<dyn Trait>`, i.e. constructor
injection), the abstraction is only adding vocabulary.

## Lens B — alternative concurrency runtime / executor

Load-bearing property: the project's chosen event loop, executor, or threading model.
Conflict if the dependency requires a different one on the core path; ready only if
it is runtime-agnostic or the conflict is confined to an opt-in feature.

## Lens C — constrained execution environment

Load-bearing property: a platform limit the code respects (no runtime/allocator,
sandboxed, size-bounded). Conflict if the dependency — or any transitive dep — pulls
the excluded surface. Check the full tree, not just the top-level dependency.

## Lens D — determinism / replay / reproducibility

Load-bearing property: no hidden non-determinism on the reproducible path. Conflict
if the dependency introduces I/O, wall-clock reads, randomness, threads, or global
mutable state where outputs must be reproducible. A purely compile-time / type-only
dependency is typically safe.

## Lens E — error / failure model

Load-bearing property: the project's failure discipline (exceptions, returned error
values, or typed error results). Conflict if the dependency forces the opposite at
the boundary.
