# Learning Studio

This is the runnable first cycle of the generalized learning system: a local,
replayable PyTorch lesson that moves from diagnosis to teaching, practice,
verification, and delayed review.

## Run it with uv

From the repository root:

```bash
uv run --locked python apps/learning-studio/server.py
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) in a browser.

**No API key is required.** With no credential, the right-rail tutor chat falls
back to a scripted, phase-aware guide, and everything else works unchanged.
Session state and events are stored in the ignored `.local/` SQLite database.
The server exposes the lesson fixture at `/api/lesson`, the concept catalog at
`/api/knowledge`, the deterministic grader at `/api/grade`, the current session
at `/api/session`, typed events at `/api/events`, and the advisory tutor at
`/api/tutor`.

## The tutor (optional, advisory)

The chat rail is backed by a model tutor when an Anthropic credential is
available (an `ANTHROPIC_API_KEY` in the environment, or an `ant auth login`
profile); otherwise it uses the scripted guide. Set the model with
`LEARNING_STUDIO_TUTOR_MODEL` (default `claude-opus-5-5`). Installing the project
environment now pulls in the `anthropic` SDK, so the app is no longer strictly
dependency-free.

The tutor is **advisory only**. It may propose a diagnosis observation, but the
proposal is recorded as a `tutor.observation.proposed` event and never enters
`evidence` — it cannot change mastery or advance a phase. The deterministic
grader in `grading.py` remains the sole owner of learner state. Every tutor
exchange is stored as events, so replaying a session reconstructs the whole
conversation with no model call.

If uv is not installed yet, follow the install instructions at
[docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/),
then rerun the command above.

## Current boundary

The verification step is still a deterministic simulated runner, but open
responses and choice activities now pass through a versioned structured grader
before their observations enter the event stream. An advisory model tutor (G4,
pulled forward) can propose diagnosis observations, but those proposals stay out
of mastery until calibration exists. The session/event substrate is durable and
replayable; a later roadmap cycle adds a bounded PyTorch execution sandbox.
