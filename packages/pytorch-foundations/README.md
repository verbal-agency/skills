# PyTorch foundations package

This package is the G2 subject artifact for the Learning Studio. It turns the
first runtime fixture into a versioned, declarative subject package covering
tensor metadata, autograd, minibatch optimization, and trustworthy evaluation.

## Validate the executable examples

From the repository root:

```bash
uv lock --directory packages/pytorch-foundations
uv run --project packages/pytorch-foundations --locked python packages/pytorch-foundations/examples/validate_examples.py
```

The package lock pins PyTorch and its transitive dependencies. The examples use
CPU-only tensors, fixed seeds, and assertions that make the evidence contract
visible. They do not constitute a sandbox for learner-submitted code.

## Artifact order

Read `scope.yaml`, `graph.json`, the six files in `concepts/`,
`diagnostics/misconceptions.yaml`, `exercises/core.yaml`, and
`curricula/core.yaml`. `evidence/events.jsonl` shows how package version,
activity, observation, and evaluator provenance fit the G1 event contract.

The audit is conditional until a real learner session supplies response and
transfer evidence.
