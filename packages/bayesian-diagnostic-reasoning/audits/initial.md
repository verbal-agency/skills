# Learning package audit

- Package: `bayesian-diagnostic-reasoning`
- Version: `0.1.1`
- Curriculum: `CUR-BAY-001`
- Intended learner: Learner with basic fractions and probability notation
- Target outcome: Interpret diagnostic test results with base-rate reasoning
- Audited at: 2026-10-31
- Verdict: `conditional`
- Allowed use, if conditional: Guided study and worked numerical exercises

## Executive finding

The package has a bounded non-clinical scope, strong source provenance, a
dependency graph, multiple representations, and checked numerical examples.
It has not yet been tested against a real learner, so teachability and transfer
remain open.

## Criterion-to-evidence

| Dimension | Criterion | Evidence or check | Result |
|---|---|---|---|
| Provenance | Definitions and diagnostic measures trace to NIST/CDC/OpenStax | `sources.jsonl`, `claims.jsonl` | pass |
| Scope | Calculation and interpretation outcomes are explicit | `scope.yaml` | pass |
| Graph | Conditional, base-rate, test, update, and decision dependencies are represented | `graph.json` | pass |
| Concepts | Units include analogy limits, counterexamples, and denominator checks | `concepts/*.yaml` | pass |
| Practice | Items test reversal, calculation, transfer, and an explicit asymmetric-cost threshold decision | `exercises/core.yaml` | pass |
| Curriculum | Modules progress from notation to update to decision | `curricula/core.yaml` | pass |
| Runtime | A learner has completed and transferred the exercises | No learner session | open |

## Findings

| ID | Severity | Artifact | Evidence | Required action | Owning skill |
|---|---|---|---|---|---|
| BAY-AUD-001 | major | `learner-state/default.yaml` | No learner responses yet | Run an interactive session and record misconception evidence | `teach-from-domain-package` |
| BAY-AUD-002 | minor | `scope.yaml` | Transfer context is unresolved | Add a spam-filter or quality-control example after first session | `design-learning-practice` |

## Freshness

Core probability claims are stable; examples and decision framing should be
reviewed for clarity after learner testing.

## Publication conditions

Upgrade to `pass` after one learner completes the diagnostic and capstone, the
conditional-reversal error is explicitly tested, and one non-medical transfer
case is added.
