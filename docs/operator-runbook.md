# Learning Studio operator runbook

This document is for the person starting, demonstrating, and resetting the
local Learning Studio runtime. The current implementation is a single-process,
dependency-light demo through G2.5: a replayable PyTorch session plus a
package-backed Knowledge surface and learner-owned exploration overlay.

## 1. Prerequisites

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) installed and available as `uv`
- A browser that can open a local address

Confirm the tools from the repository root:

```bash
uv --version
uv run --locked python --version
```

No API key, database, or model download is needed for this slice.

## 2. Start the runtime

From the repository root:

```bash
uv run --locked python apps/learning-studio/server.py
```

Keep this terminal open. The expected startup message is:

```text
Learning Studio running at http://127.0.0.1:8765
Press Ctrl-C to stop.
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) in the browser.

To use another local port:

```bash
LEARNING_STUDIO_PORT=8766 uv run --locked python apps/learning-studio/server.py
```

Then open `http://127.0.0.1:8766/`.

## 3. Run the operator smoke check

In a second terminal, while the server is running:

```bash
curl -fsS http://127.0.0.1:8765/api/lesson
curl -fsS -X POST http://127.0.0.1:8765/api/events \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"operator-check","type":"operator.smoke","phase":"diagnose","data":{"ok":true}}'
```

The first command should return the PyTorch lesson fixture. The second should
return an event with `sequence: 1` and HTTP status `201`.

Run the deterministic replay and transition checks with:

```bash
uv run --locked python apps/learning-studio/test_storage.py
```

The expected result is four passing tests. The suite proves that illegal phase
transitions are rejected and that a new store reconstructs the same state from
the recorded events, including study traces and overlays.

Session events are written to `.local/learning-studio.sqlite3`, which is
ignored by Git. To use a different local database for an isolated run:

```bash
LEARNING_STUDIO_DB=/tmp/learning-studio-check.sqlite3 \
  uv run --locked python apps/learning-studio/server.py
```

In the browser, complete the five visible phases:

1. **Diagnose:** answer why `optimizer.zero_grad()` runs before backward.
2. **Teach:** read the explanation and continue.
3. **Practice:** select `optimizer.zero_grad()` and run verification.
4. **Verify:** confirm the simulated result reports `4 / 4 passed`.
5. **Review:** explain gradient accumulation in your own words and finish.

The evidence panel should show baseline evidence, code-repair evidence, and
transfer-review evidence. The sidebar should show review scheduled for two days.

Use the **Knowledge** surface to search the six PyTorch concepts, open a card,
follow a related concept, try recall, or add a concept to the exploration
overlay. The study-trace counter should increase, but the Session evidence
panel should not: browsing and retrieval practice are preparation, not mastery.
The **Review** surface summarizes both counts separately.

## 4. Reset or replay a learner session

The browser stores demo progress under local storage. Use the **Reset session**
button in the top bar to clear the current replay and start again. A normal
refresh should preserve the current phase and evidence.

The server owns the canonical phase, evidence, and event state. Restarting the
server preserves completed events because they are replayed from SQLite. The
browser only keeps unsent drafts and UI convenience state in local storage.
The **Reset session** button clears the browser draft; it does not delete the
server database. Use a separate `LEARNING_STUDIO_DB` path for a clean isolated
run rather than deleting learner data casually.

## 5. Stop and troubleshoot

- Stop the server with `Ctrl-C` in its terminal.
- If port `8765` is occupied, set `LEARNING_STUDIO_PORT` to another local port.
- If the page is blank, check the server terminal and reload the exact URL,
  including the selected port.
- If `uv run` reports a Python-version mismatch, install or select Python 3.10+
  and rerun `uv run --locked python ...`.
- If the UI seems stuck, click **Reset session**; this removes only the local
  demo state for this browser.

## 6. Current boundary and operator expectations

- Verification is a deterministic simulated runner, not arbitrary PyTorch code
  execution.
- Events are local and durable, but this is still a single-user SQLite demo,
  not a backup or multi-user learner record.
- Knowledge cards are package-backed study aids. They do not establish
  mastery, and route proposals currently record available references rather
  than passing a full prerequisite/capability validator.
- The app binds to `127.0.0.1`; it is not a hosted or multi-user service.
- The in-app browser smoke pass covers the Knowledge card/detail flow and a
  390px narrow layout without horizontal overflow. Inspect the final desktop
  presentation manually before a polished demo if you change the CSS.
- Do not enter private learner data into a shared screen or commit browser
  storage exports to the repository.

The next cycle is G3: structured evidence and deterministic graders. Real
PyTorch execution belongs in G5, after sandbox limits and evidence semantics
are implemented.
