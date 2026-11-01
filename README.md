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
