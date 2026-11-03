# Learning package audit

- Package: `langchain-certified-agent-engineer`
- Version: `0.1.1`
- Curriculum: `CUR-LC-001`
- Intended learner: Python-capable engineer preparing for LCAE and practical agent work
- Target outcome: Build, test, deploy, and monitor one small production-shaped agent
- Audited at: 2026-11-02
- Verdict: `conditional`
- Allowed use, if conditional: Guided study, dry-run design, and official-course companion work

## Executive finding

The package is bounded to the four-domain LCAE lifecycle and now incorporates the
learner-supplied exam guide's section blueprint and focus areas. It maps official
Academy courses to concepts, practice, and a capstone. It is not yet evidence of
exam readiness or production competence because no learner session, timed practice
run, supplied LangSmith trace/evaluation artifact, or externally reported deployment
outcome has been recorded. The assistant has no direct visibility into the learner's
IDE or runtime environment.

## Criterion-to-evidence

| Dimension | Criterion | Evidence or check | Result |
|---|---|---|---|
| Provenance | Certification and course claims trace to official LangChain sources and the supplied exam guide | `sources.jsonl`, `claims.jsonl` | pass |
| Scope | Four equally weighted exam domains and their guide-listed focus areas map to observable capabilities and evidence | `scope.yaml` | pass |
| Graph | Layer, lifecycle, testing, deployment, and monitoring dependencies are represented | `graph.json` | pass |
| Concepts | Units include boundaries, representations, misconceptions, and provenance | `concepts/*.yaml` | pass |
| Practice | Items cover build, test, deploy, monitor, integrated evidence, and a timed/whitelisted practice protocol | `exercises/core.yaml` | pass |
| Curriculum | Modules sequence the lifecycle and map every capability to practice and assessment | `curricula/core.yaml` | pass |
| External execution evidence | The learner can bring code, errors, logs, traces, or reports back for diagnosis; runtime remains outside assistant visibility | Handoff policy recorded; no learner artifacts yet | major gap |

## Findings

| ID | Severity | Artifact | Evidence | Required action | Owning skill |
|---|---|---|---|---|---|
| LC-AUD-001 | major | Private learner state | No learner response data | Run a prediction-first session and record evidence in private state | `teach-from-domain-package` |
| LC-AUD-002 | major | `exercises/core.yaml`, private learner state | External tracing, evaluation, deployment, and monitoring are unexecuted and not directly observable here | Have the learner implement externally, then bring failures or artifacts back for inspection; label outcomes as reported unless reproduced | `teach-from-domain-package` |
| LC-AUD-003 | major | `exercises/core.yaml`, private learner state | The 40-question/120-minute practice protocol from the exam guide has not been run | Complete a timed practice run and record section-level misses in private state under exam-like resource restrictions | `teach-from-domain-package` |

## Freshness

Refresh the official certification page, exam guide, Academy course pages, and
product behavior within 30 days of booking or execution.

## Publication conditions

Upgrade to `pass` only after one learner completes the diagnostic and capstone,
one externally executed build/test slice is documented with supplied artifacts or
failure reports, and deployment or monitoring claims are explicitly labeled as
reported, inspected, or reproduced rather than assumed.
