#!/usr/bin/env python3
"""Small local learning-studio runtime for the first roadmap slice.

This deliberately uses only the Python standard library. It provides a static
UI, a lesson fixture endpoint, and an in-memory event endpoint so the browser
can exercise the same session/event shape that the live agent runtime will use.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
PORT = int(os.environ.get("LEARNING_STUDIO_PORT", "8765"))

LESSON = {
    "id": "pytorch-training-loop-001",
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

EVENTS: dict[str, list[dict]] = {}


def send_json(handler: BaseHTTPRequestHandler, payload: object, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[learning-studio] {self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlparse(self.path)
        if parsed.path == "/api/lesson":
            send_json(self, LESSON)
            return
        if parsed.path == "/api/events":
            session_id = parse_qs(parsed.query).get("session_id", ["demo-session"])[0]
            send_json(self, {"session_id": session_id, "events": EVENTS.get(session_id, [])})
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlparse(self.path)
        if parsed.path != "/api/events":
            send_json(self, {"error": "not_found"}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size) or b"{}")
        except (ValueError, json.JSONDecodeError):
            send_json(self, {"error": "invalid_json"}, 400)
            return
        session_id = str(payload.get("session_id", "demo-session"))
        event = {
            "sequence": len(EVENTS.setdefault(session_id, [])) + 1,
            "type": str(payload.get("type", "unknown")),
            "phase": payload.get("phase"),
            "data": payload.get("data", {}),
        }
        EVENTS[session_id].append(event)
        send_json(self, event, 201)

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
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Learning Studio running at http://127.0.0.1:{PORT}")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Learning Studio.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
