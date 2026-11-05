#!/usr/bin/env python3
"""Local learning-studio runtime with a replayable SQLite session store.

This deliberately uses only the Python standard library. It provides a static
UI, package-backed lesson and knowledge endpoints, a server-owned deterministic
grader, and an event endpoint. Session state is derived by replaying typed
events from a local SQLite database.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from grading import grade_choice, grade_open_response
from storage import SessionStore, TransitionError


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
PORT = int(os.environ.get("LEARNING_STUDIO_PORT", "8765"))
REPO_ROOT = ROOT.parent.parent
DB_PATH = Path(os.environ.get("LEARNING_STUDIO_DB", REPO_ROOT / ".local" / "learning-studio.sqlite3"))
CATALOG_PATH = REPO_ROOT / "packages" / "pytorch-foundations" / "catalog.json"
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

LESSON = {
    "id": "pytorch-training-loop-001",
    "package_id": CATALOG["package_id"],
    "package_version": CATALOG["package_version"],
    "title": "Repair a PyTorch training loop",
    "subject": "PyTorch foundations",
    "objective": "Explain why gradients are cleared before backpropagation, then repair a small training loop.",
    "skills": [
        {"id": "tensor-reasoning", "label": "Tensor reasoning", "progress": 0.72},
        {"id": "autograd", "label": "Autograd", "progress": 0.34},
        {"id": "training-loop", "label": "Training loop", "progress": 0.18},
    ],
    "phases": ["diagnose", "teach", "practice", "verify", "review"],
    "diagnostic": {
        "prompt": "Why should optimizer.zero_grad() usually run before loss.backward() in a training loop?",
        "hint": "Think about what happens to a parameter's .grad value after a backward pass.",
    },
    "practice": {
        "prompt": "Which missing line should be added before the forward pass?",
        "options": [
            "optimizer.zero_grad()",
            "model.eval()",
            "torch.softmax(logits, dim=1)",
            "loss.detach()",
        ],
        "correct": 0,
        "code": "for X, y in train_loader:\n    X, y = X.to(device), y.to(device)\n\n    logits = model(X)\n    loss = loss_fn(logits, y)\n    loss.backward()\n    optimizer.step()",
    },
    "review": {
        "prompt": "In one or two sentences, what is likely to happen if gradients are never cleared across batches?",
        "hint": "Use the word accumulate or carry over, and describe the effect on updates.",
    },
}

STORE: SessionStore


def send_json(handler: BaseHTTPRequestHandler, payload: object, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def validate_structured_observation(
    event_type: str,
    data: dict[str, object],
    provenance: dict[str, object],
) -> None:
    """Reject client-mutated structured evidence before it reaches SQLite."""

    observation = data.get("observation")
    if observation is None:
        return  # Preserve replay compatibility for pre-G3 legacy events.
    if not isinstance(observation, dict):
        raise ValueError("structured observation must be an object")
    package_version = str(provenance.get("package_version", LESSON["package_version"]))
    if event_type == "diagnostic.submitted":
        expected = grade_open_response(
            str(data.get("activity_id", "diagnostic.gradient-accumulation.baseline")),
            data.get("answer", ""),
            package_version,
        )
    elif event_type in {"practice.failed", "code.verified"}:
        expected = grade_choice(
            str(data.get("activity_id", "practice.gradient-accumulation.repair")),
            data.get("selected"),
            LESSON["practice"]["correct"],
            package_version,
        )
    elif event_type == "review.completed":
        expected = grade_open_response(
            str(data.get("activity_id", "review.gradient-accumulation.transfer")),
            data.get("answer", ""),
            package_version,
        )
        expected_result = "passed" if expected["result"] == "pass" else "failed"
        if data.get("result") != expected_result:
            raise ValueError("review result does not match the deterministic observation")
    else:
        raise ValueError(f"structured observations are not supported for event {event_type!r}")
    if observation != expected:
        raise ValueError("structured observation does not match the server grader")
    if provenance.get("evaluator") != expected["evaluator"]:
        raise ValueError("event evaluator provenance does not match the server grader")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[learning-studio] {self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlparse(self.path)
        if parsed.path == "/api/lesson":
            send_json(self, LESSON)
            return
        if parsed.path == "/api/knowledge":
            send_json(self, CATALOG)
            return
        if parsed.path == "/api/overlay":
            session_id = parse_qs(parsed.query).get("session_id", ["learning-studio-g2-session"])[0]
            snapshot = STORE.snapshot(session_id, LESSON["id"])
            send_json(self, {
                "session_id": session_id,
                "package_id": CATALOG["package_id"],
                "package_version": snapshot["package_version"] if snapshot["exists"] else LESSON["package_version"],
                "overlay": snapshot["state"]["overlay"],
                "study_traces": snapshot["state"]["study_traces"],
                "route_proposals": snapshot["state"]["route_proposals"],
            })
            return
        if parsed.path in ("/api/session", "/api/events"):
            session_id = parse_qs(parsed.query).get("session_id", ["demo-session"])[0]
            snapshot = STORE.snapshot(session_id, LESSON["id"])
            if parsed.path == "/api/events":
                send_json(self, {"session_id": session_id, "events": snapshot["events"], "state": snapshot["state"], "exists": snapshot["exists"]})
            else:
                send_json(self, snapshot)
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlparse(self.path)
        if parsed.path not in ("/api/events", "/api/grade"):
            send_json(self, {"error": "not_found"}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 256 * 1024:
                send_json(self, {"error": "payload_too_large"}, 413)
                return
            payload = json.loads(self.rfile.read(size) or b"{}")
        except (ValueError, json.JSONDecodeError):
            send_json(self, {"error": "invalid_json"}, 400)
            return
        if parsed.path == "/api/grade":
            try:
                package_version = str(payload.get("package_version", LESSON["package_version"]))
                mode = str(payload.get("mode", "open_response"))
                activity_id = str(payload.get("activity_id", ""))
                if mode == "open_response":
                    observation = grade_open_response(
                        activity_id,
                        payload.get("response", ""),
                        package_version,
                    )
                elif mode == "choice":
                    observation = grade_choice(
                        activity_id,
                        payload.get("selected_index"),
                        LESSON["practice"]["correct"],
                        package_version,
                    )
                else:
                    raise ValueError(f"unsupported grading mode: {mode}")
            except (TypeError, ValueError) as error:
                send_json(self, {"error": "invalid_grading_request", "detail": str(error)}, 400)
                return
            send_json(self, {
                "package_id": CATALOG["package_id"],
                "package_version": package_version,
                "observation": observation,
            })
            return
        session_id = str(payload.get("session_id", "demo-session"))
        provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
        provenance.setdefault("package_version", LESSON["package_version"])
        data = payload.get("data", {})
        try:
            if not isinstance(data, dict):
                raise ValueError("event data must be an object")
            validate_structured_observation(str(payload.get("type", "unknown")), data, provenance)
        except (TypeError, ValueError) as error:
            send_json(self, {"error": "invalid_event", "detail": str(error)}, 400)
            return
        try:
            result = STORE.append_event(
                session_id=session_id,
                lesson_id=LESSON["id"],
                event_type=str(payload.get("type", "unknown")),
                phase=str(payload.get("phase", "")),
                data=data,
                provenance=provenance,
            )
        except TransitionError as error:
            send_json(self, {"error": "invalid_transition", "detail": str(error)}, 409)
            return
        except ValueError as error:
            send_json(self, {"error": "invalid_event", "detail": str(error)}, 400)
            return
        send_json(self, result, 201)

    def serve_static(self, request_path: str) -> None:
        relative = "index.html" if request_path in ("", "/") else request_path.lstrip("/")
        candidate = (STATIC / relative).resolve()
        if STATIC not in candidate.parents and candidate != STATIC:
            send_json(self, {"error": "forbidden"}, 403)
            return
        if not candidate.is_file():
            send_json(self, {"error": "not_found"}, 404)
            return
        content_types = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
        }
        body = candidate.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_types.get(candidate.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    global STORE
    STORE = SessionStore(DB_PATH, LESSON["phases"])
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Learning Studio running at http://127.0.0.1:{PORT}")
    print(f"SQLite session store: {DB_PATH}")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Learning Studio.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
