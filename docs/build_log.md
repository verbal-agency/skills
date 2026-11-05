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
