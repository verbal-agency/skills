# Learning Studio build log

## G1 — Persistent session and event substrate

- **Prior limitation:** G0 kept the authoritative phase and evidence in browser
  local storage while the Python event endpoint held events in memory.
- **Capability built:** SQLite-backed sessions, append-only typed events,
  server-owned phase transitions, and deterministic replay now provide the
  session state returned to the UI.
- **Why this shape:** canonical events are durable and inspectable; browser
  drafts remain local without becoming learner-state truth.
- **Observed:** replay tests reconstruct the same phase, evidence, and event
  sequence after opening a new store against the same database.
- **What this unlocks:** structured evidence and deterministic graders can be
  added without trusting browser-controlled phase changes.
- **Does not prove:** this does not provide a real PyTorch sandbox, model-based
  diagnosis, multi-user isolation, or durable backups.

Interview explanation: “I moved session authority from local browser state into
an append-only SQLite event log, then made the current phase and evidence a
deterministic projection of that log. The next question is how the event schema
and replay rules evolve without invalidating historical learner evidence.”

## G2 — Versioned PyTorch foundations package

- **Prior limitation:** G0/G1 could render and persist one simulated PyTorch
  lesson, but the subject content lived in a hard-coded lesson fixture and the
  keyword diagnosis was not trustworthy evidence.
- **Hypothesis:** A package with a typed graph, authored concept units,
  evidence-producing activities, explicit misconception routes, and a pinned
  executable environment can drive subject content without adding controller
  branches.
- **Capability built:** `packages/pytorch-foundations/` now contains scope,
  sources, claims, graph, six concept units, six misconception records, eight
  versioned activities and solutions, a four-module curriculum, synthetic
  package-versioned evidence events, a conditional audit, and CPU examples.
- **Observed:** YAML/JSON/JSONL artifacts parse; `uv lock` resolves the package
  environment; `uv run --project packages/pytorch-foundations --locked python
  packages/pytorch-foundations/examples/validate_examples.py` passes assertions
  for metadata, a 36 gradient, decreasing training loss, and graph-free
  evaluation.
- **Interpretation:** The package contract is representable and executable,
  which retires the risk that subject content must be hard-coded into the
  controller. This does not establish grader precision, learner transfer, or a
  safe learner code sandbox; those remain explicit later goals.
- **Decision:** Advance to G3 structured evidence and deterministic graders;
  keep model diagnosis advisory until the package has independently labeled
  failure fixtures and calibration/abstention evidence.

Interview explanation: “I separated PyTorch subject knowledge from the runtime
by expressing concepts, capabilities, misconceptions, activities, rubrics, and
transfer items as versioned package artifacts. I then pinned a small CPU
environment and made the examples assert the evidence contract instead of
merely printing a plausible loss. The next question is how those rubric results
become structured observations without pretending a keyword or model score is
ground truth.”

Likely follow-up: “Why not let an LLM grade the answers now?” The answer is that
the package currently supplies authored rubrics and deterministic checks, while
the independent labeled set needed to validate a model judge does not exist
yet. The work supports package-driven content and executable examples; it does
not support claims about learner improvement or diagnosis accuracy.
