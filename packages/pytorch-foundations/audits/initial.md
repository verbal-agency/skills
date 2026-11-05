# Learning package audit

- Package: `pytorch-foundations`
- Version: `0.1.0`
- Curriculum: `CUR-PT-001`
- Intended learner: Python-capable learner preparing to debug small PyTorch research examples
- Target outcome: Trace tensors and gradients, repair a training loop, and separate evaluation evidence
- Audited at: 2026-11-04
- Verdict: `conditional`
- Allowed use, if conditional: Guided local study and executable CPU examples

## Executive finding

The package has a bounded scope, official PyTorch provenance, a typed graph,
progressive concept units, six explicit misconception records, versioned
activities, a curriculum with introduce/practice/assess/revisit coverage, and
deterministic CPU examples. It has not yet been tested with a learner, so
diagnostic precision, remediation lift, and transfer remain open.

## Criterion-to-evidence

| Dimension | Criterion | Evidence or check | Result |
|---|---|---|---|
| Provenance | Material PyTorch claims trace to current official documentation | `sources.jsonl`, `claims.jsonl` | pass |
| Scope | Tensor, autograd, training, and evaluation outcomes are bounded | `scope.yaml` | pass |
| Graph | Concepts, capabilities, and six failure modes have typed relations | `graph.json` | pass |
| Concepts | Units include progressive explanations, code checks, boundaries, and misconceptions | `concepts/*.yaml`, `diagnostics/misconceptions.yaml` | pass |
| Practice | Eight activities separate prompts, solutions, rubrics, and routes | `exercises/core.yaml`, `exercises/solutions/` | pass |
| Curriculum | Every capability has introduce, practice, assess, and revisit coverage | `curricula/core.yaml` | pass |
| Executable evidence | Pinned CPU examples assert metadata, gradients, update order, and evaluation context | `pyproject.toml`, `uv.lock`, `examples/validate_examples.py` | pass |
| Runtime provenance | Synthetic evidence events carry package and evaluator versions | `evidence/events.jsonl` | pass |
| Teachability | A learner has completed and transferred the activities | No learner session | open |

## Findings

| ID | Severity | Artifact | Evidence | Required action | Owning skill |
|---|---|---|---|---|---|
| PT-AUD-001 | major | `evidence/events.jsonl` | Events are synthetic fixtures, not learner observations | Run the package through the runtime and compare rubric labels with independent review | `teach-from-domain-package` |
| PT-AUD-002 | minor | `scope.yaml` | GPU, distributed, and mixed-precision variants are out of scope | Add transfer variants only after CPU evidence is stable | `design-learning-practice` |

## Freshness

Core autograd concepts are stable. API references, optimizer defaults, and
tutorial URLs should be refreshed within one year or when the pinned PyTorch
version changes.

## Publication conditions

Upgrade to `pass` after the examples run in the pinned environment, at least
one learner or independently labeled fixture set completes the diagnostic and
capstone, and the six misconception routes are checked for false positives and
abstention behavior.
