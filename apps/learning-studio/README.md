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
uses the project environment without installing a package. No API key or
database is required. Progress is stored in the browser's local storage for
this demo. The server exposes the lesson fixture at `/api/lesson` and records
local session events at `/api/events`.

If uv is not installed yet, follow the install instructions at
[docs.astral.sh/uv/getting-started/installation](https://docs.astral.sh/uv/getting-started/installation/),
then rerun the command above.

## Current boundary

The verification step is a deterministic simulated runner. The next roadmap
cycle adds durable session events and then replaces the simulated check with a
bounded PyTorch execution sandbox.
