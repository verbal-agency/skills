# Research and scope method

## Research lenses

Use enough independent lenses to prevent one source's navigation or commercial
framing from becoming the curriculum boundary.

| Lens | Question |
|---|---|
| Outcome | What must the learner accomplish in reality? |
| Standard | What does a certification, syllabus, regulation, or role require? |
| Lifecycle | What happens from design through operation and retirement? |
| Decisions | Which alternatives must a practitioner distinguish and choose? |
| Failures | What breaks, how is it detected, and how is it recovered? |
| Foundations | Which prerequisite disciplines explain the mechanisms? |
| Practice | Which artifacts, tools, and environments produce authentic evidence? |

## Source hierarchy

Prefer primary specifications, official documentation, source code, standards,
and original research for normative or technical claims. Use strong secondary
sources for synthesis, history, and competing explanations. Use community
material to discover vocabulary and failure modes, then verify material claims.

Record disagreement rather than averaging incompatible claims. Distinguish a
product recommendation, a current default, and a general principle.

## Source record

Store one JSON object per line in `sources.jsonl`:

```json
{"id":"SRC-001","title":"...","url":"...","publisher":"...","source_type":"primary","version":"...","published_at":"...","retrieved_at":"...","covers":["CAP-001"],"limitations":["..."]}
```

## Claim record

Store one JSON object per line in `claims.jsonl`:

```json
{"id":"CLM-001","statement":"...","kind":"fact","source_ids":["SRC-001"],"support":"direct","confidence":"high","volatility":"medium","refresh_after":"...","notes":"..."}
```

Use `kind` values `fact`, `interpretation`, `recommendation`, `assumption`, or
`dispute`. Use `support` values `direct`, `inferred`, or `contested`.

## Boundary tests

Include an area only when it is a prerequisite, directly advances a target
capability, materially affects a required decision, or represents a likely
failure the learner must handle. Route adjacent but nonessential material to an
optional branch or exclusion list.

Refresh volatile claims before a package is audited when their recorded horizon
has passed. Preserve prior source records for provenance when updating them.
