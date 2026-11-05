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

The repository includes a dependency-free `pyproject.toml`, so uv creates and
uses the project environment without installing a package. No API key is
required. Session state and events are stored in the ignored `.local/` SQLite
database. The server exposes the lesson fixture at `/api/lesson`, the concept
catalog at `/api/knowledge`, the deterministic grader at `/api/grade`, the
current session at `/api/session`, and typed events at `/api/events`.

If uv is not installed yet, follow the install instructions at
[docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/),
then rerun the command above.

## Current boundary

The verification step is still a deterministic simulated runner, but open
responses and choice activities now pass through a versioned structured grader
before their observations enter the event stream. The session/event substrate
is durable and replayable; later roadmap cycles add model-assisted proposals and
a bounded PyTorch execution sandbox.
