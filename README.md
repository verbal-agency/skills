# Theo

Theo is an evidence-based learning companion. It pairs a local **Learning
Studio** app with a toolchain of composable skills for turning a learning goal
into a researched, structured, teachable, and auditable learning package.
Subjects such as AWS infrastructure or on-premises model serving are generated
package content, not hard-coded skills.

## Pipeline

1. `scope-learning-domain` researches the field and fixes its boundary.
2. `decompose-learning-domain` builds a typed concept and capability graph.
3. `author-concept-unit` explains individual concepts through suitable representations.
4. `design-learning-practice` creates questions, exercises, and labs.
5. `assemble-learning-path` sequences the material into a curriculum.
6. `audit-learning-package` checks accuracy, coverage, coherence, and usability.
7. `teach-from-domain-package` teaches from the package and records learner evidence.

Each skill is independently invocable and exchanges explicit package artifacts
with the others. A package normally progresses through `scoped`, `modeled`,
`enriched`, `assembled`, and `audited` stages.

## First vertical-slice packages

The pipeline has been exercised on three deliberately different domains:

- [AWS three-tier VPC](packages/aws-vpc-three-tier/manifest.yaml) — network objects, traffic paths, layered controls, and two-AZ resilience.
- [Mistral on-prem serving](packages/mistral-on-prem-serving/manifest.yaml) — model profiles, tokenizer/template correctness, vLLM serving, benchmarks, and endpoint hardening.
- [Bayesian diagnostic reasoning](packages/bayesian-diagnostic-reasoning/manifest.yaml) — conditional probability, test characteristics, Bayesian updates, and decision thresholds.
- [LangChain Certified Agent Engineer](packages/langchain-certified-agent-engineer/manifest.yaml) — building, testing, deploying, and monitoring agents across the current LCAE domains.

All three are currently `assembled` with conditional audits. The remaining
evidence is intentionally explicit: live AWS and GPU serving runs, plus learner
responses and transfer evidence for the Bayesian package.

## Runnable learning studio

The first runtime slice is a local, replayable PyTorch learning session. Start
it with uv from the repository root:

```bash
uv run --locked python apps/learning-studio/server.py
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/). Operator instructions,
smoke checks, reset behavior, and current boundaries are documented in
[docs/operator-runbook.md](docs/operator-runbook.md).
