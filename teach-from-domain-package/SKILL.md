---
name: teach-from-domain-package
description: Teach interactively from a structured domain or learning package, selecting concept representations, questions, examples, and practice based on the learner's goal and demonstrated evidence. Use for tutoring, guided study, oral examination, review sessions, remediation, or continuing an existing curriculum while maintaining learner state without rewriting the source package.
---

# Teach from Domain Package

Run evidence-responsive teaching sessions from an assembled package. Preserve a
strict separation between canonical package content and learner-specific state.
When implementation happens in an environment that is not visible to the
assistant, treat execution outcomes as learner-reported unless the learner
supplies an artifact, log, trace, or error for inspection. Do not infer runtime
success from a conversation, confidence statement, or planned exercise.

## Required inputs

Read the selected curriculum, relevant concept units and exercises, package
audit status, and the learner's private state when available. Learner state is
session data, not publishable package content: keep it in an ignored
`learner-state/` directory or another private store and never commit it by
default. If no learner state exists, copy
[assets/learner-state-template.yaml](assets/learner-state-template.yaml) into
that private location. Read
[references/teaching-protocol.md](references/teaching-protocol.md) before the
first session or when changing teaching mode.

Teach from an `assembled` package when necessary, but disclose missing or failed
audit findings. Do not present disputed or stale material as settled.

## Session loop

1. **Orient.** State the target capability, why it matters, known prerequisites,
   and what observable evidence would close the session.
2. **Retrieve before revealing.** Ask a concise prediction, recall, or diagnostic
   question before presenting the answer. A skipped answer does not block the
   session; record it as missing evidence.
3. **Select one useful representation.** Start with the learner's missing model,
   not with every stored explanation. Move among gist, precise definition,
   analogy, contrast, diagram, trace, example, code, or lab when evidence shows
   the current representation is insufficient.
4. **Check interpretation.** Ask the learner to restate, predict, compare, trace,
   or apply. Avoid asking only whether the explanation made sense.
5. **Practice with fading support.** Use hints only after an attempt. Move from
   guided work toward independent performance at the required level.
6. **Diagnose errors.** Classify an error as missing prerequisite, factual gap,
   boundary confusion, faulty causal model, procedure failure, transfer failure,
   or execution slip. Choose remediation that matches the error.
7. **Require closure evidence.** Use the curriculum's rubric or capability
   criterion. Do not infer mastery from confidence, fluency, or one copied
   solution.
8. **Update learner state.** Record attempts, evidence, misconceptions, hints,
   confidence separately from performance, review timing, and the next action.
   Label evidence by observability: conceptual chat evidence, inspected artifact,
   learner-reported external result, or reproduced result.
9. **Close cleanly.** Summarize the corrected model, one limitation, what the
   evidence supports, and what remains unproven. Schedule retrieval rather than
   immediately reteaching a successful item.

## Interaction modes

Support these modes without changing the package contract:

- explanation at a requested depth;
- Socratic tutoring;
- worked-example walkthrough;
- pair debugging or lab guidance;
- oral examination;
- review and spaced retrieval;
- remediation after failed evidence;
- architecture or design defense.

Never reveal hidden solutions during an assessment unless the learner ends the
attempt or explicitly switches to teaching mode. Do not silently modify concept
content in response to a learner error. Record suspected package defects for
`audit-learning-package` or the appropriate build-time skill.
