---
name: scope-learning-domain
description: Research and bound a subject for systematic learning, producing a sourced scope, capability inventory, claim ledger, and versioned learning-package manifest. Use when starting a new learning domain, refreshing a volatile subject, translating a certification or job goal into study scope, or deciding what a curriculum must include and exclude.
---

# Scope Learning Domain

Create the evidence base and boundary for a learning package. Do not decompose
the domain into a detailed concept graph or write lessons in this skill.

## Inputs

Collect or infer the following, marking assumptions explicitly:

- desired real-world outcome and external standard, if any;
- target learner and relevant prior knowledge;
- deadline, weekly effort, budget, tools, hardware, and access constraints;
- required level of performance: recognize, explain, choose, implement,
  diagnose, design, or defend;
- source and freshness requirements.

Ask only when a missing answer would materially change the boundary. Otherwise
choose a reversible default and record it.

## Workflow

1. **Write the outcome contract.** State the learner, target capability,
   authentic situations where it is used, observable completion evidence,
   constraints, exclusions, and stop conditions.
2. **Research through independent lenses.** Cover authoritative standards or
   documentation, practitioner tasks, system lifecycle, decisions, failure
   modes, and prerequisite disciplines. Read
   [references/research-and-scope.md](references/research-and-scope.md) before
   substantial research.
3. **Create a source index.** Prefer primary and current sources for normative
   or volatile claims. Record source type, authority, version, retrieval date,
   coverage, and limitations.
4. **Create a claim ledger.** Separate sourced facts from synthesis and
   assumptions. Assign stable claim IDs. Mark volatility, confidence, and the
   source passages that support each material claim.
5. **Describe capabilities.** Use observable verbs. Cover what the learner must
   recognize, recall, explain, discriminate, apply, diagnose, design, and
   defend only where the target outcome requires those levels.
6. **Set the boundary.** Record included areas, excluded areas, adjacent areas,
   assumed prerequisites, unresolved questions, and evidence that would change
   the boundary.
7. **Check coverage.** Map every target outcome to at least one capability and
   one authoritative source. Identify unsupported or disputed areas rather
   than filling them with plausible prose.
8. **Initialize the package.** Copy and adapt
   [assets/manifest-template.yaml](assets/manifest-template.yaml) and
   [assets/scope-template.yaml](assets/scope-template.yaml). Create
   `manifest.yaml`, `scope.yaml`, `sources.jsonl`, and `claims.jsonl`. Set the
   package stage to `scoped` only after the quality gate passes.

## Package contract

Preserve stable IDs and provenance so later skills can refine without losing
traceability. Use this minimum layout:

```text
<package>/
├── manifest.yaml
├── scope.yaml
├── sources.jsonl
├── claims.jsonl
├── graph.json
├── concepts/
├── exercises/
├── curricula/
├── learner-state/
└── audits/
```

Create only the first four artifacts during scoping. Leave later directories
empty or omit them until needed.

## Quality gate

Require all of the following before declaring the package scoped:

- one unambiguous outcome contract;
- explicit inclusions, exclusions, and assumed prerequisites;
- capability statements with observable evidence;
- primary support for normative and volatile claims;
- source dates or versions for changeable material;
- a destination for every unresolved question;
- no claim that silently exceeds its source.

Report the boundary, highest-risk uncertainty, sources needing refresh, and the
recommended input for `decompose-learning-domain`.
