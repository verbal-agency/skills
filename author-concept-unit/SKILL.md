---
name: author-concept-unit
description: Author or revise one sourced learning concept using definitions, simple explanations, mental models, analogies, examples, counterexamples, diagrams, traces, code, misconceptions, and checks selected to fit the concept. Use when enriching concept stubs, creating reusable teaching material, explaining a concept at multiple depths, or repairing a weak or misleading explanation in a learning package.
---

# Author Concept Unit

Create one reusable concept unit at a time. Optimize for accurate mental models
and transfer, not for including every possible presentation format.

## Required inputs

Read the target concept stub, its prerequisite and contrast neighbors from
`graph.json`, relevant claims and sources, the target capabilities, and any
learner profile supplied by the caller. Return unresolved factual gaps to
`scope-learning-domain`; return graph boundary problems to
`decompose-learning-domain`.

Read [references/representation-strategies.md](references/representation-strategies.md)
before choosing explanation forms.

## Workflow

1. **Fix the learning target.** State what the learner should understand or do
   after the unit and what this unit intentionally does not teach.
2. **Establish the boundary.** Write a precise definition, aliases, prerequisites,
   contrasts, and the problem the concept solves. Define unavoidable technical
   terms before using them.
3. **Create progressive layers.** Provide a short gist, plain explanation,
   precise technical account, and deeper mechanics only as required by the
   target capability.
4. **Select representations.** Choose formats based on concept type and learner
   need. Prefer causal traces for mechanisms, contrasts for decisions,
   examples and counterexamples for boundaries, and executable demonstrations
   for procedures.
5. **Constrain analogies.** Map each important part of an analogy to the real
   concept and state where the analogy breaks. Omit an analogy that adds more
   distortion than insight.
6. **Ground examples.** Include at least one representative example and one
   boundary case or near miss. Explain why each qualifies.
7. **Make dynamics visible.** For stateful or causal concepts, show inputs,
   transitions, outputs, and failure behavior through a trace or diagram.
8. **Make code testable.** When code is appropriate, state the environment,
   prerequisites, command or snippet, expected result, and one failure case.
   Never use code merely as visual decoration.
9. **Target misconceptions.** Record common incorrect beliefs, why they are
   tempting, the correction, and a diagnostic question that distinguishes real
   understanding from memorized wording.
10. **Add retrieval seeds.** Add a few questions or prompts, but leave full
    exercise construction and rubrics to `design-learning-practice`.
11. **Record provenance.** Attach claim IDs and sources to factual sections.
    Mark synthesis, uncertainty, version sensitivity, and learner-specific
    adaptations explicitly.
12. **Write the unit.** Copy and adapt
    [assets/concept-unit-template.yaml](assets/concept-unit-template.yaml).

## Quality gate

Require the unit to be accurate, self-contained relative to declared
prerequisites, explicit about boundaries, and useful at more than one depth.
Verify that examples respect the definition, analogy limits are stated, code
is reproducible when present, and retrieval prompts test the intended concept.

Do not set the whole package to `enriched` until every required concept has an
approved unit or an explicit waiver.
