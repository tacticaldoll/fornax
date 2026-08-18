# Portable skill interfaces

`skill-interface.yaml` is an optional, vendor-neutral sidecar for a skill that produces or consumes
a record another skill can use. Skills that do not participate in a record handoff omit it. A
sidecar that exists is validated strictly.

The declaration supports discovery and recommendation only. It never authorizes or invokes a skill;
the host must obtain explicit user authorization after presenting a recommendation.

## Format

The file uses a deliberately small YAML subset so repository and installer checks need no YAML
dependency: a `publisher` scalar and block lists named `produces` or `consumes`. It must declare at
least one record.

```yaml
publisher: 9d0f3c1a-7b2e-4e61-8d45-2a6f90c3b817
produces:
  - 9d0f3c1a-7b2e-4e61-8d45-2a6f90c3b817/review-record@1 text/markdown
consumes:
  - 4fc6fe1e-327c-40f4-b63e-2d1999614f61/disposition-record@1 text/markdown
```

Each record is the tuple `(publisher UUID, record type, major version, media type)` rendered as:

```text
<publisher-uuid>/<record-type>@<major> <media-type>
```

- Publisher UUID is the stable identity. A producer may only produce records under its declared
  publisher; a consumer may consume records from another publisher. A collection records its own
  publisher once as `distribution.json` `publisher_id`, and validation catches sidecar drift.
- Record type uses lowercase hyphen-case and describes semantics, not a skill name.
- Major starts at 1 and changes only when an old consumer cannot read the new record.
- Media type describes representation. It is not a payload schema.

A consumer that names a producer's record in its `**Input**:` line uses the standardized form
``a `<producer>` <Title Case Record Name>`` (for example, ``a `static-review` Review Record``).
Workspace validation checks that the producer declares exactly one matching record type and that the
consumer sidecar consumes that identity. This narrow prose check catches a missing declaration; the
sidecars, not prose, remain authoritative for seam discovery.

When a producer's record is consumed by another skill, mark the Markdown fence that defines the
record's visible output shape:

````text
<!-- OUTPUT-TEMPLATE: <record-type>@<major> <media-type> -->
```markdown
...
```
````

The marker belongs immediately before the `markdown` fence. It is scoped to its own skill folder and
inherits the publisher from that folder's `skill-interface.yaml`; seam discovery matches the full
four-part record identity before using the marker to select a template inside the matched producer.
Each produced record has exactly one marked template. A missing or duplicate marker fails the seam
inventory check.

Unknown structure fails closed. Payload schemas, eligibility rules, execution instructions,
authorization, network lookup, and cryptographic publisher verification are outside version 1.

## Recommendation behavior

Build indexes locally from installed skills that opt in. Match the complete record tuple exactly.
When one consumer matches, recommend it; when several match, an explicit user preference may select
one, otherwise present the tied candidates. Repeated preferences are ordered: the first named skill
with any match wins, and duplicate installed sources for that skill remain tied rather than falling
through to a lower-ranked skill. Keep the full index out of agent context and expose it only on
demand. A recommendation is information, not permission to invoke.
