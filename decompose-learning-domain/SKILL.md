---
name: decompose-learning-domain
description: Transform a scoped learning domain into a typed graph of terms, concepts, principles, mechanisms, procedures, decisions, failure modes, capabilities, and prerequisite relationships. Use when a sourced subject scope must be decomposed, normalized, checked for gaps or cycles, or prepared for concept authoring and curriculum design.
---

# Decompose Learning Domain

Build the domain model that later skills can explain, exercise, and sequence.
Keep decomposition separate from lesson writing.

## Required inputs

Read `manifest.yaml`, `scope.yaml`, `sources.jsonl`, and `claims.jsonl`. If the
scope is absent or materially unsupported, return the gap to
`scope-learning-domain` instead of inventing a boundary.

Read [references/graph-model.md](references/graph-model.md) before modeling a
new package or changing node and edge semantics.

## Workflow

1. **Inventory candidates.** Extract terms, concepts, mechanisms, principles,
   procedures, decisions, failure modes, measurements, and capabilities from
   the scoped sources.
2. **Normalize identity.** Give each concept one stable canonical ID. Record
   aliases, acronyms, overloaded meanings, deprecated names, and source terms.
   Do not create separate concepts merely because two sources use different
   labels.
3. **Type each node.** Use the node taxonomy in the graph reference. Split a
   node when it bundles independently teachable ideas or independently
   assessable capabilities.
4. **Define concise stubs.** Write a one-sentence boundary definition and the
   problem or role each concept serves. Avoid full explanations at this stage.
5. **Add typed relationships.** Use `requires`, `is-a`, `part-of`, `contrasts-with`,
   `implements`, `causes`, `prevents`, `measured-by`, `used-to-decide`, and
   `commonly-confused-with`. Add a new relation type only with defined semantics.
6. **Map capabilities.** Connect every capability to the concepts it requires
   and the evidence expected at each cognitive level. A topic list without
   capabilities is incomplete.
7. **Form subject clusters.** Group concepts for navigation without treating
   clusters as prerequisites. Permit a concept to support multiple clusters.
8. **Validate the model.** Detect undefined references, duplicate meanings,
   circular hard prerequisites, orphan concepts, unsupported capabilities,
   capabilities with no concept support, and scope items absent from the graph.
9. **Write artifacts.** Adapt
   [assets/concept-graph-template.json](assets/concept-graph-template.json),
   create one stub per concept under `concepts/`, and set the package stage to
   `modeled` only after validation passes.

## Modeling rules

- Treat a term as a label and a concept as its meaning.
- Treat a subject as a navigational cluster, not an atomic concept.
- Use `requires` only for genuine learning prerequisites; use other relations
  for association.
- Preserve disputes and alternative models instead of forcing false consensus.
- Attach claim IDs to nodes and edges that assert factual relationships.
- Keep volatile product names or versions separate from stable principles when
  doing so improves reuse.
- Do not sequence lessons here. Graph order and teaching order are different.

## Completion report

Report node and edge counts by type, unresolved terminology, cycles or gaps,
capability coverage, concepts ready for authoring, and concepts blocked on
additional research.
