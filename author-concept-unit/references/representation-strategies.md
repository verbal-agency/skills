# Representation strategies

Select representations to repair a specific missing mental model. More formats
do not automatically produce a better unit.

| Need or concept type | Prefer | Verify |
|---|---|---|
| Boundary or definition | examples, counterexamples, contrast | learner classifies a new case |
| Mechanism | causal explanation, state trace, diagram | learner predicts a changed input |
| Procedure | demonstration, code, expected output, failure | learner completes and debugs it |
| Decision | scenario, comparison, tradeoff table | learner chooses and defends |
| Principle | varied examples, analogy, transfer case | learner applies it in a new domain |
| Failure mode | symptoms, causal chain, diagnosis, recovery | learner distinguishes similar failures |
| Measurement | calculation, interpretation, misleading case | learner states what it cannot prove |

## Progressive depth

Use a layered structure when several audiences or depths are required:

1. **Gist:** one or two sentences answering what and why.
2. **Working model:** enough structure to reason about ordinary cases.
3. **Precise account:** exact boundaries, vocabulary, and mechanism.
4. **Operational view:** how it appears in code, tools, or artifacts.
5. **Limits and tradeoffs:** edge cases, failure, uncertainty, and alternatives.

Do not make the gist false in ways the deeper explanation must later undo.

## Analogy contract

State the source situation, map its important parts to the target, name the
insight it provides, and explain at least one place the mapping fails. Avoid an
analogy when the learner must unlearn its central causal model.

## Example contract

Explain why an example qualifies. Pair representative examples with boundary
cases, counterexamples, or near misses. Vary irrelevant surface features so the
learner cannot succeed through visual pattern matching alone.

## Code contract

Include environment, dependencies, complete invocation, expected output,
observable success, and a meaningful failure. Prefer the smallest executable
example that preserves the concept's real behavior.
