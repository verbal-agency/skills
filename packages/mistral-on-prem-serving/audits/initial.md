# Learning package audit

- Package: `mistral-on-prem-serving`
- Version: `0.1.1`
- Curriculum: `CUR-MIS-001`
- Intended learner: Engineer with basic Linux, Python, HTTP, and GPU terminology
- Target outcome: Deploy and evaluate one private Mistral endpoint
- Audited at: 2026-10-31
- Verdict: `conditional`
- Allowed use, if conditional: Research planning, dry-run configuration, and conceptual study

## Executive finding

The package separates model selection, input formatting, serving, capacity, and
security concerns and uses current primary sources. It cannot yet claim a
working deployment because no target hardware, runtime version, or live endpoint
has been recorded.

## Criterion-to-evidence

| Dimension | Criterion | Evidence or check | Result |
|---|---|---|---|
| Provenance | Volatile Mistral and vLLM claims have dated sources | `sources.jsonl`, `claims.jsonl` | pass |
| Scope | Four capabilities and exclusions are explicit | `scope.yaml` | pass |
| Graph | Model, input, serving, capacity, and security dependencies are represented | `graph.json` | pass |
| Concepts | Units include code or operational traces where appropriate | `concepts/*.yaml` | pass |
| Practice | Profile, serve, benchmark, and diagnose tasks exist; a profile template, benchmark harness, and endpoint-check artifacts are included | `exercises/core.yaml`, `profiles/`, `labs/` | pass |
| Curriculum | Modules progress from profile to serving to measurement | `curricula/core.yaml` | pass |
| Runtime | GPU load, output quality, endpoint exposure, and benchmark are tested | Not run | major gap |

## Findings

| ID | Severity | Artifact | Evidence | Required action | Owning skill |
|---|---|---|---|---|---|
| MIS-AUD-001 | major | `learner-state/default.yaml` | Target hardware is unknown | Record host, GPU, VRAM, runtime, and model revision | `scope-learning-domain` |
| MIS-AUD-002 | major | `exercises/core.yaml`, `labs/` | Server, benchmark, and security checks are still unexecuted | Run the selected serving command, `labs/benchmark.py`, and `labs/verify-private-endpoint.sh` on the recorded host | `design-learning-practice` |

## Freshness

Refresh model, license, vLLM flag, and hardware claims before execution. Treat
the package as version-sensitive by default.

## Publication conditions

Upgrade to `pass` after one reproducible endpoint run, a tokenizer/template
check, a benchmark artifact, and a network/auth boundary test are recorded.
