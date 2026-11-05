# Study notes

## G1 review questions

1. Why should learner state be derived from events instead of stored as the
   only truth? **Answer:** Events preserve the observed facts and let a
   projection change without rewriting history. A projection-only state would
   hide which response or tool result caused a phase or evidence change.
2. Which events are sufficient to reconstruct the current phase and evidence?
   **Answer:** The current fixture needs the session start, diagnostic
   submission, phase-scoped activity completions, practice/code results, and
   review completion, with event phase, data, package version, and sequence
   preserved. Replay derives phase and evidence from those typed events.
3. How should an event-schema change preserve replayability for old sessions?
   **Answer:** Keep old event shapes readable, add an explicit schema version
   or adapter, and test replay against a recorded old stream before changing
   the projection. Do not silently reinterpret an old field.

## Concepts to review

- Event sourcing: storing facts first and deriving a current projection.
- SQLite transaction boundaries: making sequence allocation and transition
  validation atomic.
- Authority boundaries: keeping unsent browser drafts separate from canonical
  server-owned session state.

## G2 review questions

1. Which PyTorch package claims are stable principles, and which need refresh
   when the pinned environment or API version changes?
2. How can a rubric distinguish a stale-gradient misconception from an
   intentional microbatch accumulation policy?
3. Which independent labels and transfer variants would be sufficient to
   test whether the six misconception routes abstain when evidence is sparse?

## G2.5 review questions

1. Why are `concept.viewed` and `flashcard.attempted` stored separately from
   `activity.graded` and `assessment.passed`? What product mistake would happen
   if card exposure counted as mastery?
2. Which parts of a learner-owned overlay should be replayable facts (selected
   concepts, rationale, package version), and which should remain a derived
   view?
3. Before G3, what deterministic checks should reject a route proposal: missing
   prerequisites, unavailable practice references, stale package version, or
   something else?
