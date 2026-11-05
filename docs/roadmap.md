# Learning Studio Roadmap

## Project outcome

Turn the repository's learning-package pipeline into a runnable learning studio
that can explore concepts with a learner, shape a useful route when needed,
diagnose a learner's gap, provide targeted practice, verify the result, and
schedule a later transfer check. PyTorch is the first validation subject
because it provides both didactic explanations and executable evidence.
Bayesian diagnostic reasoning is the second validation subject because it
exercises the same interaction model without code execution.

## Primary consumer

One learner using a local web application, plus the package author who needs to
inspect why an activity, diagnosis, or remediation was selected.

## Canonical scenarios

- **S0 — Explore and shape:** The learner riffs with the tutor about a goal or
  curiosity, sees linked concepts and possible next activities, and optionally
  saves the emerging route as a curriculum overlay.
- **S1 — Start learning:** The learner opens the studio, selects a skill, and
  sees a clear objective and a short diagnostic.
- **S2 — Learn through evidence:** The learner receives an explanation, attempts
  an activity, and sees grounded feedback rather than a generic answer.
- **S3 — Repair a gap:** A wrong or uncertain response is classified, routed to
  a narrower intervention, and retested with a new item.
- **S4 — Transfer later:** A review item is scheduled and, when due, tests the
  same capability with different surface details.
- **S5 — Add a subject:** A second subject package uses the same runtime and UI
  without subject-specific branches in the session controller.

## Architecture constraints

- Keep the existing package stages: `scoped`, `modeled`, `enriched`,
  `assembled`, `audited`, and `taught`.
- Treat each package version as immutable during learner sessions. Conversation
  and learner evidence may create candidate concepts, gap observations,
  misconception hypotheses, source suggestions, and exercise proposals; an
  accepted addition creates a new package version rather than mutating the old
  one.
- Use the typed concept graph as the primary navigation model. A curriculum
  path is an optional saved projection over that graph, not a prerequisite for
  every session.
- Allow a session route to be a single concept, a short linked sequence, a
  goal-driven path, a gap-driven repair, a review item, or constrained
  interest-guided roulette. The route policy must explain why a next activity
  was selected and must respect prerequisites.
- Keep learner-specific overlays, route proposals, and candidate package
  contributions separate from canonical package artifacts until explicitly
  promoted and reviewed.
- Make the session controller deterministic; let Claude generate explanations,
  prompts, hints, and feedback within the controller's allowed phase.
- Store evidence events separately from derived mastery state.
- Treat diagnosis confidence as provenance, not as a number a model is allowed
  to invent. Every probabilistic score must name its evaluator, version,
  calibration set, and evidence references; uncalibrated scores cannot change
  mastery.
- Let deterministic graders produce pass/fail or categorical results rather
  than pretending they are probabilities. Use calibrated probabilities only
  when held-out labeled cases support them.
- Run PyTorch examples in a bounded local sandbox; network access is disabled
  by default.
- Keep private learner traces local. Public examples use synthetic fixtures.
- Start with a dependency-light local app; add hosted infrastructure only after
  the interaction loop has evidence of value.

## Evidence and confidence contract

The runtime records an observation, not an unquestioned diagnosis. A diagnosis
observation has this shape:

```yaml
label: gradient_accumulation
status: candidate              # candidate | supported | confirmed | abstained
score: 0.82                     # optional; only for calibrated probabilities
confidence_source:
  type: calibrated_model        # deterministic | calibrated_model | human | derived
  evaluator_id: rubric-pt-001
  evaluator_version: 1
  calibration_set: pt-diagnosis-v1
  calibration_size: 48
evidence_refs: [EV-104, EV-109]
evidence_spans: ["the previous batch carries over"]
alternatives: [backward_order_confusion]
```

The example score is not a model's self-reported certainty. It would come from
an evaluator tested on held-out labeled responses, then calibrated so that a
score has an interpretable meaning. A deterministic test should instead record
`type: deterministic` and its exact result. A learner-state service may derive
confidence from repeated, independent observations, but it must store the
formula and source observations. When evidence is sparse or conflicting, the
diagnoser abstains or emits `status: candidate`.

## Failure-data strategy

Do not begin by assuming that a large external corpus is required. Seed each
subject with an expert-reviewed failure library containing misconception
definitions, positive and negative signals, confusable alternatives,
disambiguating questions, remediation, and transfer items. Expand it with
synthetic cases, anonymized local responses when permitted, structured code-run
failures, and public material only when its license and privacy terms allow it.
Model-generated labels are proposals for review, not ground truth. Keep a
held-out evaluation set for diagnosis precision, recall, abstention,
calibration, and remediation/transfer lift.

## Roadmap goals

### G0 — Runnable learning-studio shell (complete)

Build a local web app with a real session layout and a replayable PyTorch lesson
fixture. The first slice must be useful without an API key.

Acceptance criteria:

- `uv run --locked python apps/learning-studio/server.py` starts a local web
  server from a clean checkout.
- The browser renders objective, skill progress, tutor activity, learner input,
  hints, and an evidence panel.
- The fixture can move through `diagnose → teach → practice → verify → review`.
- A browser refresh preserves the current session in local storage.

Unlocks: live agent integration without changing the UI contract.

The current G0 fixture intentionally uses a brittle keyword heuristic and a
simulated code check. Those are UI probes, not trusted learner evidence.

### G1 — Persistent session and event substrate (complete)

Move session authority from browser-only state into a local SQLite store while
keeping the event stream append-only and replayable.

Acceptance criteria:

- A schema migration creates sessions, events, package versions, and review
  records in an ignored local database.
- Illegal phase transitions are rejected by the server.
- Every learner response and tool result becomes a typed event with provenance.
- The current phase and activity survive a server restart.
- Replaying the event stream reconstructs the same session state.

Unlocks: reliable diagnosis and model-assisted evaluation without trusting
browser state.

G1 evidence: `apps/learning-studio/storage.py`, the three replay/transition
 tests in `test_storage.py`, the API restart probe, and the browser smoke pass
 against the persisted session projection.

### G2 — PyTorch subject package (complete)

Create `packages/pytorch-foundations/` using the repository's existing package
schemas. Start with tensor reasoning, autograd, and training/evaluation loops.

Acceptance criteria:

- Scope, graph, concepts, exercises, solutions, curriculum, claims, sources,
  and audit artifacts exist.
- Every required capability has introduce/practice/assess/revisit coverage.
- Examples execute in a pinned environment.
- At least six misconception records have signals, confusable alternatives,
  disambiguators, remediation, and transfer items.
- The package version is recorded on every activity and evidence event.

Unlocks: package-driven activity rendering.

G2 evidence: `packages/pytorch-foundations/` contains the versioned package
artifacts, six misconception records, eight activities with separate
solutions/rubrics, curriculum coverage, synthetic evidence fixtures, and a
pinned CPU environment. `uv run --project packages/pytorch-foundations
--locked python packages/pytorch-foundations/examples/validate_examples.py`
passes the executable evidence checks. The audit remains conditional until a
learner or independently labeled fixture set exercises the routes.

### G2.5 — Conversational concept navigator and curriculum overlays

Build the conversation layer that turns package knowledge and learner intent
into exploratory concept neighborhoods, short route proposals, and optional
saved curriculum overlays. Do not require a complete path before the learner
can investigate one concept.

Acceptance criteria:

- A learner can state a goal or curiosity and receive linked concepts and at
  least two plausible next-activity options grounded in the active package
  version.
- The learner can branch, return, request a prerequisite, ask for a transfer
  item, or choose constrained interest-guided roulette without losing the
  canonical package boundary.
- The system stores a draft overlay with learner intent, selected concepts,
  route rationale, assumptions, open questions, and package version separately
  from the package itself.
- A deterministic validator checks prerequisite readiness, capability coverage,
  activity availability, and package-version compatibility for every proposed
  route.
- Explicit promotion creates a versioned curriculum overlay or a candidate
  package contribution; conversation never silently rewrites canonical content.
- Draft, branch, promotion, and contribution events replay from the G1 SQLite
  event substrate and render through the existing UI contract.

Unlocks: learner-shaped study without forcing every interaction into a
full-fledged path, and a safe intake point for gaps and curiosities that may
later improve the subject package.

### G3 — Structured evidence and deterministic graders

Replace the keyword diagnosis and hard-coded success path with versioned
rubrics and evidence observations.

Acceptance criteria:

- Open-ended answers produce structured observations with evidence spans,
  alternatives, status, and evaluator provenance.
- Deterministic activities produce exact categorical results rather than
  invented probabilities.
- Replay fixtures cover knowledge gap, misconception, procedural error,
  transfer failure, and execution slip.
- A seeded labeled set reports diagnosis precision, recall, abstention, and
  calibration before the grader can affect learner state.

Unlocks: a defensible model-assisted diagnostician.

### G4 — Model-assisted diagnosis

Add an optional model judge for explanations and ambiguous failures. The model
may propose a diagnosis observation, but the controller owns phase transitions,
mastery updates, and remediation selection.

Acceptance criteria:

- The model returns schema-valid labels, evidence spans, alternatives,
  uncertainty, model version, and prompt version.
- Model scores are calibrated on held-out labeled cases or the model abstains
  from numeric confidence.
- Conflicting or low-confidence observations trigger a disambiguating item,
  not a mastery update.
- Replaying recorded model outputs produces the same derived state without a
  live model call.

Unlocks: adaptive explanations without making the model the source of truth.

### G5 — PyTorch code lab

Add a bounded workspace, code runner, hidden tests, and structured run results.

Acceptance criteria:

- The learner can edit and run a starter example.
- A broken training loop produces a diagnostic test result.
- Correct code produces a verifiable evidence event.
- Time, memory, filesystem, and network limits are enforced.

Unlocks: executable evidence and code-specific remediation.

### G6 — Remediation and delayed review

Select targeted interventions and structurally different follow-up items from
the package and evidence store.

Acceptance criteria:

- A suspected misconception requires more than one independent supporting
  signal before it becomes confirmed.
- Failed diagnostics route to a narrower lesson or exercise.
- A follow-up item changes surface details while preserving the target skill.
- A simulated clock selects due reviews from the learner's open gaps.
- Review results update the mastery state and close or extend the gap.
- Evidence can propose a learner-overlay revision or a candidate package
  contribution; it cannot silently mutate the canonical package version.

Unlocks: measurable learning outcomes rather than conversational satisfaction.

### G7 — Second-subject validation

Run the same UI, event model, evidence schema, and session engine against the
existing Bayesian diagnostic reasoning package.

Acceptance criteria:

- A non-code activity renders without changing the session controller.
- The system diagnoses conditional-reversal or base-rate confusion.
- It provides targeted remediation and a non-medical transfer item.
- The package audit can move beyond “no learner responses observed.”

Unlocks: evidence that the architecture generalizes beyond PyTorch.

### G8 — Subject adapter contract and refresh

Make activity types, graders, sources, and optional tools declarative and
versioned. Add source refresh and re-audit workflows.

Acceptance criteria:

- Adding a subject requires a package and adapter configuration, not core
  runtime branches.
- Source updates identify affected concepts and exercises.
- Historical learner evidence remains interpretable against its package version.
- Synthetic end-to-end evals cover S0 through S5.

Unlocks: safe expansion to additional technical and didactic subjects.

## Stop and pivot conditions

- If G0 cannot run locally without external services, reduce the dependency
  surface before adding agent integration.
- If G5 cannot guarantee sandbox boundaries, use a simulated runner and keep
  execution evidence explicitly marked as simulated.
- If G3 or G4 cannot distinguish misconceptions from isolated slips, do not add
  subjects; improve the evidence contract first.
- If G7 requires subject-specific branches in the core controller, revisit the
  adapter contract instead of duplicating the runtime.
- If a model judge cannot produce calibrated scores or reliable abstentions,
  keep it advisory and do not let it update mastery.
- If route generation requires a complete path before the first useful
  interaction, reduce it to a concept-level or short-sequence proposal.
- If conversational additions lack provenance or a review state, keep them as
  provisional contributions and do not use them as trusted evidence.

## Current implementation boundary

G0, G1, and G2 are complete. The next cycle is G2.5: the conversational
concept navigator and curriculum overlays. G3 remains the following goal;
model-assisted diagnosis and real code execution remain later goals and should
not be smuggled into route authoring.

## Next cycle stub — G2.5

- **Objective:** let conversation navigate the active concept graph and create
  learner-specific curriculum overlays without requiring a complete path.
- **Completed dependencies:** G0 runnable shell, G1 SQLite event substrate,
  G2 PyTorch package and authored misconception routes.
- **Project outcomes and scenarios:** advances S0 Explore and shape, S1 Start
  learning, and S5 Add a subject while preserving the package/runtime boundary.
- **Consumer:** the learner choosing what to investigate and the package author
  reviewing why a route or contribution was proposed.
- **Outcome hypothesis:** concept-level navigation plus optional saved overlays
  will preserve conversational exploration while making selected routes,
  assumptions, and package contributions inspectable.
- **Disconfirming evidence:** the system cannot explain route selection, loses
  replayability across branches, or requires subject-specific controller
  branches to render a selected activity.
- **Downstream unlock:** G3 deterministic graders can attach evidence to either
  a short exploratory route or a promoted overlay; G6 can revise overlays from
  observed gaps.
- **Stop condition:** after two repair attempts or three consecutive slices, if
  the design still forces full paths or produces untraceable roulette, reopen
  the product contract and pivot to a smaller concept-level navigator.
- **Carried-forward findings:** candidate package additions need provenance and
  review state; the package version must be attached to every route proposal,
  activity, and evidence event.

## Following goal stub — G3

- **Objective:** replace the G0 keyword diagnosis and simulated success path
  with versioned rubrics, evidence observations, and deterministic checks that
  can be replayed without a model call.
- **Dependency:** G2.5 route and overlay events must reference activity IDs and
  package versions, but G3 may grade a single concept activity without a saved
  path.
- **Outcome hypothesis:** structured observations with evidence spans,
  alternatives, evaluator provenance, and abstention will make diagnosis
  auditable without allowing an uncalibrated score to update mastery.
- **Downstream unlock:** advisory model diagnosis with a held-out evaluation
  set.
