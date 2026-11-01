# Concept graph model

## Node types

| Type | Meaning | Atomicity test |
|---|---|---|
| term | A label or notation | Can be resolved to one or more meanings |
| concept | A reusable idea or category | Can be defined and bounded independently |
| principle | A general rule or invariant | Applies across multiple cases |
| mechanism | A causal or state-changing operation | Has inputs, transitions, and outputs |
| procedure | An ordered way to perform a task | Can succeed or fail under stated conditions |
| decision | A choice among alternatives | Has criteria, constraints, and tradeoffs |
| failure-mode | A recognizable way a system or model breaks | Has causes, symptoms, and mitigations |
| measurement | A quantity or observation | Has meaning, method, and interpretation limits |
| capability | Observable learner performance | Can be assessed with direct evidence |
| subject | A navigational cluster | Groups nodes but is not a prerequisite itself |

Split nodes that require different definitions, prerequisites, or assessment.
Keep a single node when the difference is merely an alias or presentation depth.

## Edge semantics

- `requires`: the target cannot reasonably be learned without the source.
- `is-a`: the source is a specialization of the target.
- `part-of`: the source is a structural component of the target.
- `contrasts-with`: comparing the nodes reveals a meaningful boundary.
- `implements`: the source realizes the target principle or abstraction.
- `causes`: the source materially produces the target state or event.
- `prevents`: the source reduces or blocks the target failure or event.
- `measured-by`: the target is observed through the source measurement.
- `used-to-decide`: the source informs the target decision.
- `commonly-confused-with`: learners plausibly conflate the nodes.
- `supports-capability`: the source concept is required for the target capability.

Orient `requires` from dependent to prerequisite. Check cycles only across hard
`requires` edges. A cycle usually means the nodes need splitting, the edge is
associative rather than prerequisite, or the concepts require a shared simpler
foundation.

## Validation questions

- Does every in-scope capability have supporting concepts?
- Does every required concept advance a capability?
- Can each concept be defined using only its prerequisite closure?
- Are product versions separated from stable mechanisms where useful?
- Are disputes modeled as disputes rather than silently resolved?
- Are aliases searchable without becoming duplicate nodes?
