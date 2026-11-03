# Learning skills

This repository contains composable skills for turning a learning goal into a
researched, structured, teachable, and auditable learning package. Subjects
such as AWS infrastructure or on-premises model serving are generated package
content, not hard-coded skills.

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

- [AWS three-tier VPC](/Users/wcu/Desktop/portfolio/skills/packages/aws-vpc-three-tier/manifest.yaml) — network objects, traffic paths, layered controls, and two-AZ resilience.
- [Mistral on-prem serving](/Users/wcu/Desktop/portfolio/skills/packages/mistral-on-prem-serving/manifest.yaml) — model profiles, tokenizer/template correctness, vLLM serving, benchmarks, and endpoint hardening.
- [Bayesian diagnostic reasoning](/Users/wcu/Desktop/portfolio/skills/packages/bayesian-diagnostic-reasoning/manifest.yaml) — conditional probability, test characteristics, Bayesian updates, and decision thresholds.
- [LangChain Certified Agent Engineer](/Users/wcu/Desktop/portfolio/skills/packages/langchain-certified-agent-engineer/manifest.yaml) — building, testing, deploying, and monitoring agents across the current LCAE domains.

All three are currently `assembled` with conditional audits. The remaining
evidence is intentionally explicit: live AWS and GPU serving runs, plus learner
responses and transfer evidence for the Bayesian package.
