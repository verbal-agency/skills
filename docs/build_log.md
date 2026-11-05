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

## G2.5 — Conversational concept navigator and curriculum overlays

- **Prior limitation:** G2 made the PyTorch package authoritative for authored
  content, but the runtime still exposed one hard-coded lesson. Learner
  curiosity, card study, and route choices had nowhere to live without either
  mutating the package or being lost in the browser.
- **Hypothesis:** A small package-backed concept catalog plus append-only study
  traces and learner-owned overlay events can preserve conversational
  exploration while keeping canonical content versioned and inspectable.
- **Capability built:** Added `catalog.json` with six linked concepts and
  definitions; added Knowledge, Session, and Review surfaces; added concept
  search/filter/detail/related links, recall practice, overlay save, and route
  proposal actions; added `concept.viewed`, `flashcard.attempted`,
  `overlay.updated`, and `route.proposed` replay semantics; and added the
  `/api/knowledge` and `/api/overlay` endpoints.
- **Observed:** Four storage tests pass, including a restart replay test that
  preserves the selected concept and study trace while leaving graded evidence
  empty. The catalog parses, the browser bundle passes a Node syntax check,
  `git diff --check` is clean, and a local HTTP probe confirms the Knowledge and
  overlay endpoints and package-version provenance. The in-app browser smoke
  pass verified card/detail rendering, recall reveal, overlay save, zero
  mastery evidence, and a 390px layout with no horizontal overflow.
- **Interpretation / attribution confidence:** High confidence that the
  event/storage and package-boundary behavior is implemented; moderate
  confidence that the visual hierarchy is usable because the browser smoke
  inspected the rendered Knowledge flow, search rerender, focus styling, and
  390px layout. This slice does not prove that conversational route proposals
  are useful, that definitions teach mastery, or that a model can diagnose
  failures.
- **Decision:** Mark G2.5 complete for the package-backed navigator and
  learner-owned overlays. Keep route generation deterministic and advisory;
  defer conversation-generated package contributions, prerequisite validation,
  and model diagnosis to later goals.

Interview explanation: “I added a package-backed Knowledge surface without
turning browsing into mastery. Card views and retrieval attempts are separate
study traces; overlay and route events carry the active package version and
replay through SQLite. That lets a learner riff through concepts while keeping
canonical content immutable and makes the next step—structured grading—safe to
add without rewriting the interaction model.”

Likely follow-up: “How do you know the route is good?” The answer is that this
slice does not claim to know yet: it records the rationale and available
activity references, while G3 will add deterministic prerequisite/capability
checks and structured evidence. A model may later propose explanations, but it
cannot silently promote an overlay or update mastery.

## G3 — Structured evidence and deterministic graders

- **Prior limitation:** G0/G2.5 classified open responses in browser code and
  treated a hard-coded practice success object as evidence. There was no
  structured abstention path, evaluator provenance, or seeded failure set.
- **Hypothesis:** A versioned deterministic rubric can produce inspectable
  observations for a bounded PyTorch skill before any model judge is trusted.
- **Capability built:** Added `grading.py` with open-response and choice
  graders; added `/api/grade`; moved diagnostic, practice, and transfer review
  grading behind the server boundary; recorded structured observations and
  evaluator provenance in SQLite replay; added ten seeded labeled cases and a
  reproducible evaluation report.
- **Observed:** Four grader tests and five storage tests pass. The seeded report
  gives macro precision 1.0, macro recall 1.0, abstention rate 0.3, and
  `calibration.status: not_applicable`. The HTTP probe returned a supported
  baseline observation, a categorical procedural failure, replayed the
  observation plus deterministic evaluator metadata into the event stream, and
  rejected a tampered label with HTTP 400 before append.
- **Interpretation / attribution confidence:** High confidence that the API,
  event, and replay boundaries are deterministic for this authored slice;
  moderate confidence in the rubric itself because the ten cases are synthetic
  and intentionally narrow. These metrics validate fixture agreement, not
  learner diagnosis accuracy or transfer.
- **Decision:** Mark G3 complete for the first deterministic evidence slice.
  Preserve abstention and categorical results, report calibration as not
  applicable until numeric scores have held-out labels, and route model
  proposals to G4 as advisory only.

Interview explanation: “I moved grading behind the server and made it return a
versioned observation: label, status, evidence spans, alternatives, and the
deterministic evaluator that produced it. A seeded fixture set exercises a gap,
misconception, procedural error, transfer failure, and execution slip, while
the event log stores the observation for replay. The next question is how a
model proposal can disagree safely without becoming the source of truth.”

Likely follow-up: “Does the 1.0 precision/recall mean the grader works?” The
answer is no: it means the implementation matches its ten synthetic labels.
The work supports a replayable evidence contract and explicit abstention; it
does not support generalization, calibrated probabilities, learner improvement,
or model diagnosis accuracy.
