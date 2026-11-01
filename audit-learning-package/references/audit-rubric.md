# Learning package audit rubric

## Severity

- **Blocking:** unsafe, materially false, unusable, or incapable of supporting
  the stated outcome.
- **Major:** likely to cause a substantial gap or misconception for the target
  learner, or leaves a required capability without valid evidence.
- **Minor:** localized quality issue that does not invalidate the intended use.
- **Observation:** useful information without a required change.

## Audit dimensions

### Provenance and freshness

- Trace material claims to sources with appropriate authority.
- Distinguish fact, interpretation, recommendation, assumption, and dispute.
- Check volatile claims against their refresh horizon.
- Verify that a source supports the exact breadth of the claim.

### Scope and graph

- Map outcomes to capabilities and capabilities to supporting concepts.
- Verify node identity, aliases, types, edge semantics, and hard-prerequisite DAG.
- Find orphan concepts, unsupported capabilities, and unmodeled requirements.

### Concept quality

- Check definition boundaries and declared prerequisites.
- Check progressive layers for consistency rather than later contradiction.
- Check representation fit, example validity, analogy limits, and misconception
  diagnostics.
- Execute code or mark it explicitly unverified.

### Practice validity

- Match each item to its capability and cognitive level.
- Verify solvability, answer separation, plausible distractors, rubric quality,
  hint leakage, variants, and accessibility.
- Execute labs or identify the untested operational risk.

### Curriculum coherence

- Check prerequisite order, cognitive load, early usefulness, spiraling,
  interleaving, remediation, effort, environment, and final integration.
- Verify introduce-practice-assess-revisit coverage for every required capability.

### Runtime usability

- Simulate a novice explanation, misconception, failed exercise, remediation,
  and advanced transfer task.
- Verify that learner state can record evidence without mutating canonical
  package content.

## Verdict

Use `pass` only when every required criterion has direct evidence and no
blocking or major finding remains. Use `conditional` only with a precise allowed
use and risk boundary. Otherwise use `fail`.
