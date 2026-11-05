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

## UI and interaction contract

The interface must make the learning state easy to scan without turning the
screen into a dense dashboard. The current three-column session page is a
functional probe, not the visual target.

- Use three clear surfaces: **Knowledge** for concept cards and definitions,
  **Session** for interactive activities, and **Review** for due practice and
  learner evidence.
- Keep the default view calm: one primary task, generous spacing, readable
  line length, restrained color, and a clear visual hierarchy. Avoid relying on
  all-caps labels, tiny text, saturated panels, or color alone to communicate
  state.
- Make the concept browser useful at a glance: searchable tiles show concept
  name, one-line definition, cluster, and related concepts; the detail view
  reveals plain and precise explanations, examples, counterexamples,
  misconceptions, sources, and practice actions.
- Let a learner move from a card to practice, add the concept to an overlay,
  follow a graph link, or return to the conversation without losing context.
- Preserve keyboard navigation, visible focus, sufficient contrast, readable
  mobile layout, and a no-animation/reduced-motion preference.
- Treat visual polish as acceptance evidence: run a browser smoke pass at
  desktop and narrow widths, inspect empty/loading/error states, and verify
  that the primary action is obvious without reading every panel.

## Study-trace contract

The system distinguishes preparation from mastery evidence:

```text
concept.viewed       -> exposure
flashcard.attempted  -> retrieval practice
concept.explained    -> self-explanation practice
activity.graded      -> evidence
assessment.passed    -> mastery candidate
```

Viewing, bookmarking, or browsing a definition may guide recommendations, but
cannot update mastery. Study traces remain separate from graded evidence and
carry the active package version.

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

### G2.5 — Conversational concept navigator and curriculum overlays (complete)

Build the conversation layer that turns package knowledge and learner intent
into exploratory concept neighborhoods, short route proposals, and optional
saved curriculum overlays. Do not require a complete path before the learner
can investigate one concept.

Acceptance criteria:

- A learner can open the Knowledge surface with searchable concept tiles, read
  a definition and related explanations, and see at least two package-backed
  next-activity options from the selected concept, then launch a flashcard,
  practice item, or overlay action from the detail view.
- Card views and retrieval attempts create study-trace events without being
  treated as mastery evidence.
- The system stores a draft overlay with learner intent, selected concepts,
  route rationale, assumptions, open questions, and package version separately
  from the package itself.
- Overlay, route-proposal, and study-trace events replay from the G1 SQLite
  event substrate with active package-version provenance.
- The UI renders Knowledge, Session, and Review surfaces with searchable empty
  states, visible focus styling, readable narrow-width layout, and no
  horizontal overflow in the browser smoke pass.

Deferred follow-ons (not required for this slice): conversational candidate
concepts, prerequisite/capability route validation, branch and transfer
selection, explicit promotion to a versioned overlay or package contribution,
and replay of those promotion/contribution events. These belong to G3, G6,
and G8 after structured evidence exists.

Unlocks: learner-shaped study without forcing every interaction into a
full-fledged path, and a safe intake point for gaps and curiosities that may
later improve the subject package.

G2.5 evidence: `packages/pytorch-foundations/catalog.json` provides the
runtime-readable concept catalog; `/api/knowledge` and the Knowledge surface
render searchable cards, definitions, related concepts, recall practice, and
route actions; `/api/overlay` exposes the replayed overlay and study traces;
`apps/learning-studio/test_storage.py` verifies traces and overlays survive a
store restart without adding mastery evidence; and the API probe confirms the
HTTP event contract preserves the package version and overlay state. The
in-app browser smoke pass verified the Knowledge card/detail flow, recall
reveal, overlay action, zero-mastery separation, and a 390px narrow layout
without horizontal overflow.

Criteria result: the package-backed Knowledge surface, study-trace separation,
overlay replay, route proposal metadata, and package-version compatibility are
implemented. Conversation-generated concept candidates, deterministic route
validation, explicit promotion, and model-assisted diagnosis remain later
work; this slice records only learner-selected overlays and proposals.

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
- A seeded labeled set reports diagnosis precision, recall, and abstention;
  its calibration report explicitly records `not_applicable` for this
  categorical grader, and no numeric confidence can affect learner state.

Unlocks: a defensible model-assisted diagnostician.

### G4 — Model-assisted diagnosis (complete for categorical advisory slice)

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

**Criteria result:** the advisory tutor produces schema-valid proposals (label,
evidence spans, alternatives, model, prompt version) via structured outputs;
categorical proposals deliberately carry no numeric confidence; and recorded
proposals replay without a live model call and never enter `evidence`.
Conflicts, deterministic abstentions, and model abstentions now emit a
replayable `tutor.disambiguation.requested` event with an authored clarifying
item. The request remains advisory and cannot change learner state. A broader
held-out agreement study for model proposal quality remains a future evaluation
slice rather than a reason to invent a confidence score.

### G4.5 — Agent runtime orchestration

Introduce Anthropic's Agents SDK as an orchestration layer after the advisory
tutor and evidence contracts are stable. The agent may select bounded,
subject-provided tools for explanation, concept retrieval, diagnostic
clarification, quiz generation, and remediation proposals, while the session
controller remains the only authority for evidence, phase transitions, mastery,
and persistence.

Dependencies: G4's advisory tutor contract and validated model-diagnosis
criteria. This goal does not make the agent a grader and does not add arbitrary
code execution; those remain separate concerns.

Acceptance criteria:

- A provider-neutral agent adapter can run one tutor interaction through the
  Agents SDK while preserving the existing structured tutor response and event
  schemas.
- Every tool is typed, allow-listed by the active subject package, and routed
  through controller validation; the agent cannot write learner state or the
  SQLite store directly.
- Agent turns, tool calls, tool results, model identifier, SDK version, and
  prompt version are recorded with enough provenance to replay derived state
  without a live model call.
- The no-credential scripted fallback still works, and tests use recorded
  fixtures rather than a live provider.
- At least one end-to-end flow demonstrates agent-selected clarification or
  remediation without changing mastery until deterministic evidence accepts it.

Unlocks: bounded code-lab tools in G5 and agent-selected remediation/review in
G6 without moving authority into the model runtime.

Hypothesis: an explicit agent loop will support multi-step teaching and tool
use without sacrificing replayability or evidence authority.

Disconfirming evidence: tool calls require unrestricted permissions, agent
trajectories cannot be replayed deterministically, latency/cost exceeds the
local learning workflow, or the SDK adds complexity without improving a
multi-step interaction over the direct tutor adapter.

Stop condition: if the SDK cannot preserve the existing event and structured
output contracts after two bounded integration attempts, keep the direct tutor
adapter and defer agent orchestration rather than weakening the authority
boundary.

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

G0, G1, G2, G2.5, G3, and the categorical advisory slice of G4 are complete.
G4 now records model proposals and conflict/abstention disambiguation requests
without allowing them to change mastery or phase. The three-pane cockpit UI
(subject rail + topic roulette, center workspace, right-rail tutor chat) landed
alongside this tutor. G4.5 is the next agent-runtime goal; the Agents SDK must
orchestrate bounded tools rather than replace the controller or grader. Real
code execution (G5) remains a later goal and should not be smuggled into route
authoring or grading.

## Completed cycle record — G2.5

- **Objective:** let conversation navigate the active concept graph, provide a
  calm Knowledge surface for concept study, and create learner-specific
  curriculum overlays without requiring a complete path.
- **Completed dependencies:** G0 runnable shell, G1 SQLite event substrate,
  G2 PyTorch package and authored misconception routes.
- **Project outcomes and scenarios:** advances S0 Explore and shape, S1 Start
  learning, and S5 Add a subject while preserving the package/runtime boundary.
- **Consumer:** the learner choosing what to investigate and the package author
  reviewing why a route or contribution was proposed.
- **Outcome hypothesis:** concept-level navigation, useful pre-mastery cards,
  and optional saved overlays will preserve conversational exploration while
  making selected routes, study traces, assumptions, and package contributions
  inspectable.
- **Disconfirming evidence:** the system cannot explain route selection, loses
  replayability across branches, requires subject-specific controller branches
  to render a selected activity, or leaves the learner unable to scan and read
  the Knowledge surface comfortably.
- **Downstream unlock:** G3 deterministic graders can attach evidence to either
  a short exploratory route or a promoted overlay; G6 can revise overlays from
  observed gaps.
- **Stop condition:** after two repair attempts or three consecutive slices, if
  the design still forces full paths or produces untraceable roulette, reopen
  the product contract and pivot to a smaller concept-level navigator.
- **Carried-forward findings:** candidate package additions need provenance and
  review state; the package version must be attached to every route proposal,
  study trace, activity, and evidence event; card exposure must not be counted
  as mastery.

## Activated goal contract — G3 (completed)

- **Objective:** replace the G0 keyword diagnosis and simulated success path
  with versioned rubrics, evidence observations, and deterministic checks that
  can be replayed without a model call.
- **Dependency:** G2.5 route and overlay events must reference activity IDs and
  package versions, but G3 may grade a single concept activity without a saved
  path.
- **Project outcomes and scenarios:** advances S2 Learn through evidence and
  S3 Repair a gap while preserving S0's exploratory route choices.
- **Consumer:** the learner needs actionable feedback; the package author
  needs to inspect why a response was classified and whether the evaluator is
  trustworthy.
- **Outcome hypothesis:** structured observations with evidence spans,
  alternatives, evaluator provenance, and abstention will make diagnosis
  auditable without allowing an uncalibrated score to update mastery.
- **Disconfirming evidence:** the same labeled response changes category across
  replay, deterministic checks cannot distinguish an isolated slip from a
  misconception, or the seeded evaluation set cannot measure abstention and
  calibration independently of the implementation fixtures.
- **Downstream unlock:** advisory model diagnosis with a held-out evaluation
  set.
- **Stop condition:** after two repair attempts or three consecutive slices,
  if the evaluator still cannot produce stable, inspectable observations,
  stop and reopen the evidence contract rather than adding a model judge.
- **Carried-forward findings:** keep study traces separate from graded
  evidence; preserve package-version provenance; treat route proposals as
  advisory until prerequisite and capability checks exist; use the six authored
  misconception records as the initial labeled failure library.

## Completed cycle record — G3

- **Objective:** replace the browser keyword diagnosis and hard-coded success
  path with versioned, replayable deterministic evidence observations.
- **Completed dependencies:** G2.5 package-backed concepts, overlay events, and
  package-version provenance; G2 authored misconception records and activity
  rubrics.
- **Project outcomes and scenarios:** advances S2 Learn through evidence and
  S3 Repair a gap while preserving S0's exploratory route choices.
- **Consumer:** the learner receives actionable categorical feedback; the
  package author can inspect the exact signals, alternatives, and evaluator
  version behind an observation.
- **Outcome hypothesis:** a deterministic, abstaining grader with a seeded
  labeled set can make the evidence contract auditable before any model judge
  is allowed to participate.
- **Observed:** `/api/grade` returns structured observations with labels,
  statuses, evidence spans, alternatives, and deterministic evaluator
  provenance. The ten-case fixture reports macro precision 1.0, macro recall
  1.0, abstention rate 0.3, and calibration `not_applicable`. API replay stores
  the observation and evaluator metadata in SQLite without a model call; a
  tampered observation is rejected with HTTP 400 before append.
- **Interpretation:** high confidence that the runtime boundary is now
  server-owned and replayable for this authored slice; low confidence that the
  rubric generalizes beyond its ten synthetic cases. The metrics are fixture
  validation, not learner diagnosis accuracy.
- **Decision:** mark G3 complete for the first deterministic rubric slice. Keep
  numeric confidence unavailable, keep model diagnosis advisory, and route
  broader labels, calibration, and ambiguity handling to G4/G6.
- **Disconfirming evidence:** a replay changes an observation, the API permits
  a client-supplied evaluator to override the server result, or the fixture
  report stops distinguishing abstention from a classified failure.
- **Downstream unlock:** G4 can add a model proposal channel that is compared
  against the deterministic observation and held-out labels rather than
  silently changing mastery.
- **Stop condition:** after two repair attempts or three consecutive slices, if
  the rubric remains unstable or the synthetic fixture cannot expose an
  evaluator disagreement, reopen the evidence contract before adding model
  calls.
- **Carried-forward findings:** expand the labeled set with independently
  reviewed variants; add explicit disagreement handling; preserve the
  `not_applicable` calibration result until numeric scores have a held-out
  calibration set.

## Completed cycle record — G4

- **Objective:** add an advisory model tutor whose proposals cannot directly
  change phase, mastery, or remediation state, and route model/deterministic
  disagreement or abstention to a clarifying item.
- **Completed dependencies:** G3 structured observations, evaluator provenance,
  abstention, and seeded fixture report remain replayable without a live model
  call.
- **Project outcomes and scenarios:** advances S2 Learn through evidence and S3
  Repair a gap while preserving S0's route exploration.
- **Consumer:** the package author can inspect a model proposal, the
  deterministic comparison, and the reason a narrower item was requested.
- **Observed:** `tutor.observation.proposed` and
  `tutor.disambiguation.requested` replay through SQLite; disambiguation
  requests remain outside `evidence`; the model path emits no numeric score;
  and 8 storage, 4 grader, and 9 tutor tests pass.
- **Interpretation:** high confidence in the event/replay and authority
  boundary for this authored lesson; low confidence in general model proposal
  quality because no held-out live-model agreement study has been run.
- **Decision:** mark the categorical advisory slice complete. Keep proposals
  advisory, keep numeric confidence unavailable, and route agent orchestration
  to G4.5. A broader proposal-quality evaluation remains a future goal input.
- **Disconfirming evidence:** a replay changes a request, a disambiguator enters
  mastery evidence, or a model proposal changes phase without a deterministic
  controller event.
- **Downstream unlock:** G4.5 can wrap the tutor contract in an agent runtime;
  G6 can later consume accepted evidence rather than raw model proposals.
- **Carried-forward findings:** validate labels and evidence spans against the
  active package before trusting proposals; preserve package/model/prompt
  provenance; keep chat turns atomic and private.

## Active goal contract — G4.5 (Agent runtime orchestration)

- **Objective:** run one bounded tutor interaction through Anthropic's Agents
  SDK while preserving the existing structured response, event, replay, and
  controller-authority contracts.
- **Dependency:** the completed categorical advisory G4 slice and its
  no-numeric-confidence boundary.
- **Project outcomes and scenarios:** advances S0 Explore and shape, S2 Learn
  through evidence, and S3 Repair a gap.
- **Consumer:** the learner receives coherent multi-step tutoring; the package
  author can inspect tool selection and the controller's resulting decision.
- **Outcome hypothesis:** an explicit agent loop improves multi-step teaching
  and tool use without moving evidence authority into the model runtime.
- **Disconfirming evidence:** the SDK requires unrestricted tools, agent traces
  cannot replay, or latency/cost is worse than the direct tutor adapter without
  improving a canonical scenario.
- **Downstream unlock:** bounded code-lab tools in G5 and agent-selected
  remediation/review in G6.
- **Stop condition:** after two bounded integration attempts, preserve the
  direct tutor adapter and defer the SDK if the existing contracts cannot be
  maintained.
- **Carried-forward findings:** tools must be typed and allow-listed by the
  subject package; the agent cannot write SQLite or mastery state directly;
  tests use recorded fixtures rather than a live provider.
