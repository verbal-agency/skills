---
name: audit-learning-package
description: Audit a learning package for source fidelity, freshness, scope coverage, graph integrity, explanation quality, exercise validity, curriculum coherence, accessibility, and operational usability. Use before publishing or teaching a package, after material changes, when learners expose defects, or when independent evidence is needed to decide whether a package is ready.
---

# Audit Learning Package

Verify the package artifact by artifact. Do not infer readiness from polished
prose, file presence, or a successful lesson alone.

## Inputs and independence

Read the package manifest, scope, sources, claims, graph, required concept units,
exercise sets, curricula, prior audits, and changed files. Preserve the authored
artifacts during audit unless the caller separately authorizes repairs.

Read [references/audit-rubric.md](references/audit-rubric.md) before a full audit.
Copy [assets/audit-report-template.md](assets/audit-report-template.md) for the
report.

## Workflow

1. **Fix the audit target.** Record package version, intended learner, target
   outcome, required curriculum, changed surface, and applicable rubric.
2. **Check provenance.** Trace every material factual claim to an appropriate
   source. Verify quotations or paraphrases, source authority, versions,
   retrieval dates, uncertainty, and refresh policy.
3. **Check scope.** Map target outcomes to capabilities and explicit inclusions.
   Identify required material that is absent and present material that cannot
   justify its place.
4. **Check graph integrity.** Verify IDs, types, edge semantics, aliases, hard
   prerequisite acyclicity, capability mappings, and the absence of unexplained
   or orphan nodes.
5. **Check concept units.** Verify definitions, prerequisite assumptions,
   progressive explanation, representation fit, example boundaries, analogy
   limits, misconception treatment, and claim provenance.
6. **Check executable material.** Run code and technical labs where safe and
   feasible. Verify environment, expected output, failure cases, cleanup,
   safety, cost limits, and alternatives for unavailable infrastructure.
7. **Check practice validity.** Verify alignment, cognitive level, solvability,
   distractors, answer separation, rubrics, hint leakage, repeatability, and
   accessibility.
8. **Check curriculum coherence.** Verify prerequisite order, cognitive load,
   spiraling, interleaving, authentic practice, remediation, effort estimates,
   and final evidence coverage.
9. **Sample teachability.** Walk through representative paths, including a
   novice explanation, a misconception, a failed exercise, and an advanced
   transfer task. Record defects instead of compensating silently.
10. **Classify findings.** Use `blocking`, `major`, `minor`, or `observation`.
    Route each finding once to the responsible skill and artifact.
11. **Decide readiness.** Use `pass`, `conditional`, or `fail`. Set the package
    stage to `audited` only when no blocking or major finding remains and every
    required criterion has direct evidence.

## Completion rule

Provide a criterion-to-evidence table, commands or checks performed, untested
surfaces, freshness horizon, findings with owners, and the exact conditions for
publication. A conditional verdict must name its allowed use and unresolved
risk; it is not equivalent to a pass.
