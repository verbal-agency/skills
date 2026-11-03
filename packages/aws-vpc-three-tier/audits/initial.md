# Learning package audit

- Package: `aws-vpc-three-tier`
- Version: `0.1.1`
- Curriculum: `CUR-AWS-001`
- Intended learner: Learner with basic IP and HTTP knowledge
- Target outcome: Design and defend a secure, resilient three-tier VPC
- Audited at: 2026-10-31
- Verdict: `conditional`
- Allowed use, if conditional: Guided study, diagrams, and offline reasoning exercises

## Executive finding

The package has a coherent scope, typed graph, sourced concept units, practice,
and curriculum coverage. It is not yet ready to claim operational AWS mastery
because the live traffic-failure lab and cost evidence have not been executed.

## Criterion-to-evidence

| Dimension | Criterion | Evidence or check | Result |
|---|---|---|---|
| Provenance | Material AWS claims trace to primary docs | `sources.jsonl`, `claims.jsonl` | pass |
| Scope | Four target capabilities and the included gateway-endpoint decision have explicit evidence | `scope.yaml`, `curricula/core.yaml`, `concepts/gateway-endpoint-path.yaml` | pass |
| Graph | Hard prerequisite graph is acyclic and capability mappings exist | `graph.json` inspection | pass |
| Concepts | Units include definitions, contrasts, examples, misconceptions, and provenance | `concepts/*.yaml` | pass |
| Practice | Items span discrimination, diagnosis, design, and defense | `exercises/core.yaml` | pass |
| Curriculum | Modules introduce, practice, assess, and revisit required capabilities | `curricula/core.yaml` | pass |
| Runtime | Live lab and operational evidence are demonstrated | Not run | major gap |

## Findings

| ID | Severity | Artifact | Evidence | Required action | Owning skill |
|---|---|---|---|---|---|
| AWS-AUD-001 | major | `exercises/core.yaml` | Live lab is deferred | Run a disposable broken-return-path lab and record artifacts | `design-learning-practice` |

## Freshness

Refresh AWS console behavior and exam mappings before use for a current
certification plan. Detailed billing remains outside this package's scope;
stable networking principles have a longer horizon.

## Publication conditions

Upgrade to `pass` after the live lab is executed, its artifact is linked from
learner state, and no new failure modes appear.
