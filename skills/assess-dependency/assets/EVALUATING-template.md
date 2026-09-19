# Evaluating <DEPENDENCY> for this repo

A self-contained worksheet. Run the scope gate, the six evaluation dimensions, and
reach one of four decisions. Each dimension is language-neutral; Rust terms appear
only as marked examples — translate them to your ecosystem. Replace `<DEPENDENCY>`
and fill each section from *this* repo — grep results and file citations, not the
dependency's own claims.

**What it is.** <one line: what the dependency is and the mechanism it uses>

**Decision drivers.** <after filling the sheet, name the 1–2 dimensions that decided it>

---

## Scope gate

Is `<DEPENDENCY>` a **structural** dependency (shapes how code is written/composed —
abstraction layer, framework, runtime, capability system, substrate), or a **leaf
utility** (self-contained, called at a few sites, reversible)?

- Leaf utility → **stop.** Ordinary judgment applies (works / maintained / license).
  This worksheet is overkill.
- Structural → continue.

## 1. Pain existence

```sh
# grep for the duplication / boilerplate / missing guarantee this would replace
```

- Does the pain exist here, by search? <yes/no + evidence>
- Already solved by a shared module everyone imports (e.g. in Rust a `*-core` crate)? <yes/no>

## 2. Mechanism vs. load-bearing property

- This repo's load-bearing properties: <composition/substitutability model? concurrency runtime? constrained execution environment? determinism? error model? memory/ownership model? — e.g. in Rust: object-safety/dyn, executor, no_std, borrow model>
- Does the mechanism contradict one? <which, and is it on the core path?>

## 3. Boundary feasibility

- Can you legally attach the dependency's contract to the types you have? <yes/no — e.g. in Rust, orphan rule; elsewhere sealed/final classes or no monkey-patching>
- Frozen/vendored substrate in the way? <yes/no>
- License + supply-chain gate pass? <yes/no — e.g. in Rust, deny.toml, registry/source, MSRV>

## 4. Governance placement

- Stated priority order (PROJECT.md / AGENTS.md / governance)? <quote or "inferred from architecture">
- Adoption protects core contract / spine / only ergonomics-integration? <which tier>
- Contradicts any settled design stance? <yes/no>

## 5. Cost, maturity, reversibility, idiom-retreat tell

- Maturity — shipped and proven, or pre-1.0 / unreleased / roadmap-only? <…>  (unshipped → defer; the rest is moot)
- Dependency-tree / minimum-toolchain / build-time delta: <… — e.g. in Rust, proc-macro & MSRV impact>
- Exit cost / lock-in / blast radius: <…>
- Idiom-retreat tell — does its advanced tier converge back to what you already do by hand? <…>

## 6. Earn the abstraction (N≥2)

- Does this imply a shared layer across consumers? <yes/no>
- If yes: how many real consumers with observed overlap? <N>  (N=1 → this-repo-only; N≥2 → extract the overlap into a consumer-side module)

## Decision (pick one)

- [ ] **Adopt** — pain exists, mechanism fits, feasible, governance-justified, cost acceptable.
- [ ] **Adopt narrowly** — adopt only <which part>; disqualified: <which, why>; scoped to this repo.
- [ ] **Defer** — revisit when <explicit trigger: N≥2 / pain materializes / blocker clears>.
- [ ] **Decline** — <pain already solved | mechanism disqualifying>. A successful outcome.
