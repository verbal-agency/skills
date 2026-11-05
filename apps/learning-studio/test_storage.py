#!/usr/bin/env python3
"""Replay and transition tests for the Learning Studio event substrate."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from storage import SessionStore, TransitionError


PHASES = ["diagnose", "teach", "practice", "verify", "review"]


class SessionStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.store = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_event_replay_reconstructs_same_state_after_new_store(self) -> None:
        session_id = "replay-test"
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {"lesson_id": "lesson-v1"})
        self.store.append_event(
            session_id,
            "lesson-v1",
            "diagnostic.submitted",
            "diagnose",
            {"diagnosis": "promising_model"},
        )
        self.store.append_event(session_id, "lesson-v1", "tool.result", "teach", {"tool": "lesson-renderer", "ok": True})
        self.store.append_event(session_id, "lesson-v1", "activity.completed", "teach", {"concept": "x"})
        self.store.append_event(
            session_id,
            "lesson-v1",
            "code.verified",
            "practice",
            {"tests_passed": 4, "tests_total": 4},
        )
        self.store.append_event(session_id, "lesson-v1", "activity.completed", "verify", {})
        first = self.store.snapshot(session_id, "lesson-v1")
        restarted = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)
        second = restarted.snapshot(session_id, "lesson-v1")
        self.assertEqual(first["state"], second["state"])
        self.assertEqual(first["events"], second["events"])
        self.assertEqual(second["state"]["phase"], "review")

    def test_illegal_transition_is_rejected(self) -> None:
        with self.assertRaises(TransitionError):
            self.store.append_event("invalid", "lesson-v1", "activity.completed", "teach", {})
        self.store.append_event("invalid", "lesson-v1", "session.started", "diagnose", {})
        with self.assertRaises(TransitionError):
            self.store.append_event("invalid", "lesson-v1", "code.verified", "diagnose", {})

    def test_review_completion_creates_due_review_and_cannot_repeat(self) -> None:
        session_id = "review-test"
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {})
        self.store.append_event(session_id, "lesson-v1", "diagnostic.submitted", "diagnose", {})
        self.store.append_event(session_id, "lesson-v1", "activity.completed", "teach", {})
        self.store.append_event(session_id, "lesson-v1", "code.verified", "practice", {})
        self.store.append_event(session_id, "lesson-v1", "activity.completed", "verify", {})
        result = self.store.append_event(session_id, "lesson-v1", "review.completed", "review", {"result": "passed"})
        self.assertTrue(result["state"]["review_scheduled"])
        with self.assertRaises(TransitionError):
            self.store.append_event(session_id, "lesson-v1", "review.completed", "review", {"result": "passed"})


if __name__ == "__main__":
    unittest.main()
