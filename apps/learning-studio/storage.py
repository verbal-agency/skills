"""SQLite-backed event storage and deterministic session replay for G1/G3."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = 1


class TransitionError(ValueError):
    """Raised when an event is not legal for the current session phase."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_state(phases: list[str]) -> dict[str, Any]:
    return {
        "phase": phases[0],
        "phase_index": 0,
        "evidence": [],
        "study_traces": [],
        "overlay": {"title": "Exploration draft", "concept_ids": [], "package_version": None},
        "route_proposals": [],
        "hints_used": 0,
        "review_scheduled": False,
    }


class SessionStore:
    """Append events to SQLite and derive session state by replaying them."""

    def __init__(self, path: Path, phases: list[str]) -> None:
        self.path = Path(path)
        self.phases = phases
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def migrate(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS package_versions (
                    package_version TEXT PRIMARY KEY,
                    lesson_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    lesson_id TEXT NOT NULL,
                    package_version TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(package_version) REFERENCES package_versions(package_version)
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    package_version TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    evaluator_json TEXT,
                    UNIQUE(session_id, sequence),
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY(package_version) REFERENCES package_versions(package_version)
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    source_event_id INTEGER NOT NULL,
                    due_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY(source_event_id) REFERENCES events(id)
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (SCHEMA_VERSION, utc_now()),
            )

    def snapshot(self, session_id: str, lesson_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            session = connection.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            events = self._load_events(connection, session_id)
            state = replay_events(events, self.phases)
            return {
                "exists": session is not None,
                "session_id": session_id,
                "lesson_id": session["lesson_id"] if session else lesson_id,
                "package_version": session["package_version"] if session else lesson_id,
                "state": state,
                "events": events,
            }

    def append_event(
        self,
        session_id: str,
        lesson_id: str,
        event_type: str,
        phase: str,
        data: dict[str, Any],
        provenance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not session_id or len(session_id) > 200:
            raise ValueError("session_id must be between 1 and 200 characters")
        if not isinstance(data, dict):
            raise ValueError("event data must be an object")
        provenance = provenance if isinstance(provenance, dict) else {}
        package_version = str(provenance.get("package_version", lesson_id))
        actor = str(provenance.get("actor", "learner-ui"))
        evaluator = provenance.get("evaluator")
        occurred_at = utc_now()

        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            session = connection.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if session is not None and session["package_version"] != package_version:
                raise TransitionError("event package version does not match the session package version")
            events = self._load_events(connection, session_id)
            state = replay_events(events, self.phases)
            validate_transition(
                state=state,
                event_type=event_type,
                phase=phase,
                has_session=session is not None,
                phases=self.phases,
            )

            if session is None:
                connection.execute(
                    "INSERT OR IGNORE INTO package_versions(package_version, lesson_id, created_at) VALUES (?, ?, ?)",
                    (package_version, lesson_id, occurred_at),
                )
                connection.execute(
                    "INSERT INTO sessions(session_id, lesson_id, package_version, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (session_id, lesson_id, package_version, occurred_at, occurred_at),
                )
            sequence = len(events) + 1
            connection.execute(
                "INSERT OR IGNORE INTO package_versions(package_version, lesson_id, created_at) VALUES (?, ?, ?)",
                (package_version, lesson_id, occurred_at),
            )
            cursor = connection.execute(
                """
                INSERT INTO events(
                    session_id, sequence, type, phase, data_json, occurred_at,
                    package_version, actor, evaluator_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    sequence,
                    event_type,
                    phase,
                    json.dumps(data, sort_keys=True),
                    occurred_at,
                    package_version,
                    actor,
                    json.dumps(evaluator, sort_keys=True) if evaluator is not None else None,
                ),
            )
            event_id = cursor.lastrowid
            if event_type == "review.completed" and data.get("result") == "passed":
                due_at = (datetime.now(timezone.utc) + timedelta(days=2)).replace(microsecond=0).isoformat()
                connection.execute(
                    "INSERT INTO reviews(session_id, source_event_id, due_at) VALUES (?, ?, ?)",
                    (session_id, event_id, due_at),
                )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (occurred_at, session_id),
            )
            connection.commit()

        result = self.snapshot(session_id, lesson_id)
        result["event"] = result["events"][-1]
        return result

    def _load_events(self, connection: sqlite3.Connection, session_id: str) -> list[dict[str, Any]]:
        rows = connection.execute(
            "SELECT * FROM events WHERE session_id = ? ORDER BY sequence ASC", (session_id,)
        ).fetchall()
        events: list[dict[str, Any]] = []
        for row in rows:
            evaluator = json.loads(row["evaluator_json"]) if row["evaluator_json"] else None
            events.append(
                {
                    "id": row["id"],
                    "sequence": row["sequence"],
                    "type": row["type"],
                    "phase": row["phase"],
                    "data": json.loads(row["data_json"]),
                    "at": row["occurred_at"],
                    "package_version": row["package_version"],
                    "actor": row["actor"],
                    "evaluator": evaluator,
                }
            )
        return events


def validate_transition(
    state: dict[str, Any],
    event_type: str,
    phase: str,
    has_session: bool,
    phases: list[str],
) -> None:
    current = state["phase"]
    if event_type == "session.started":
        if has_session:
            raise TransitionError("session has already started")
        if phase != phases[0]:
            raise TransitionError(f"session.started must begin in {phases[0]}")
        return
    if not has_session:
        raise TransitionError("session must start before recording other events")
    if phase != current:
        raise TransitionError(f"event phase {phase!r} does not match current phase {current!r}")
    allowed = {
        "hint.used": {"diagnose", "review"},
        "diagnostic.submitted": {"diagnose"},
        "activity.completed": {"teach", "verify"},
        "tool.result": set(phases),
        "practice.failed": {"practice"},
        "code.verified": {"practice"},
        "review.completed": {"review"},
        "concept.viewed": set(phases),
        "flashcard.attempted": set(phases),
        "concept.explained": set(phases),
        "overlay.updated": set(phases),
        "route.proposed": set(phases),
    }
    if event_type not in allowed or current not in allowed[event_type]:
        raise TransitionError(f"event {event_type!r} is not legal in phase {current!r}")
    if event_type == "review.completed" and state["review_scheduled"]:
        raise TransitionError("review is already complete for this session")


def replay_events(events: list[dict[str, Any]], phases: list[str]) -> dict[str, Any]:
    state = default_state(phases)
    for event in events:
        event_type = event["type"]
        data = event.get("data", {})
        if event_type == "hint.used":
            state["hints_used"] += 1
        elif event_type == "diagnostic.submitted":
            evidence = data.get("observation") or data.get("evidence") or _diagnostic_evidence(data.get("diagnosis"))
            state["evidence"].append(evidence)
            state["phase_index"] = phases.index("teach")
        elif event_type == "activity.completed" and event["phase"] == "teach":
            state["phase_index"] = phases.index("practice")
        elif event_type == "practice.failed":
            if data.get("observation"):
                state["evidence"].append(data["observation"])
        elif event_type == "code.verified":
            evidence = data.get("observation") or data.get("evidence") or {
                "kind": "good",
                "title": "Code repair verified",
                "detail": f"{data.get('tests_passed', 0)} / {data.get('tests_total', 0)} simulated tests passed; procedural evidence recorded.",
            }
            state["evidence"].append(evidence)
            state["phase_index"] = phases.index("verify")
        elif event_type == "activity.completed" and event["phase"] == "verify":
            state["phase_index"] = phases.index("review")
        elif event_type == "review.completed":
            if data.get("result") == "passed":
                state["evidence"].append(data.get("observation") or data.get("evidence") or {
                    "kind": "good",
                    "title": "Transfer review passed",
                    "detail": "Explains the failure mode on a new prompt.",
                })
                state["review_scheduled"] = True
                state["phase_index"] = phases.index("review")
            elif data.get("observation"):
                state["evidence"].append(data["observation"])
        elif event_type in {"concept.viewed", "flashcard.attempted", "concept.explained"}:
            state["study_traces"].append({"type": event_type, **data})
        elif event_type == "overlay.updated":
            overlay = data.get("overlay")
            if isinstance(overlay, dict):
                state["overlay"] = overlay
        elif event_type == "route.proposed":
            state["route_proposals"].append(data)
    state["phase"] = phases[state["phase_index"]]
    return state


def _diagnostic_evidence(diagnosis: str | None) -> dict[str, str]:
    understands = diagnosis == "promising_model"
    return {
        "kind": "good" if understands else "warn",
        "title": "Baseline: promising model" if understands else "Baseline: suspected gap",
        "detail": "Mentions gradient carry-over or clearing." if understands else "Needs a targeted explanation of gradient accumulation.",
    }
