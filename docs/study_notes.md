# Study notes

## G1 review questions

1. Why should learner state be derived from events instead of stored as the
   only truth?
2. Which events are sufficient to reconstruct the current phase and evidence?
3. How should an event-schema change preserve replayability for old sessions?

## Concepts to review

- Event sourcing: storing facts first and deriving a current projection.
- SQLite transaction boundaries: making sequence allocation and transition
  validation atomic.
- Authority boundaries: keeping unsent browser drafts separate from canonical
  server-owned session state.
