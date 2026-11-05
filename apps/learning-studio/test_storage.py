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

    def test_study_traces_and_overlay_replay_without_mastery_evidence(self) -> None:
        session_id = "knowledge-test"
        package_version = "0.1.0"
        provenance = {"package_version": package_version, "actor": "knowledge-ui"}
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {}, provenance)
        self.store.append_event(
            session_id,
            "lesson-v1",
            "concept.viewed",
            "diagnose",
            {"concept_id": "CON-PT-001", "trace_kind": "exposure"},
            provenance,
        )
        self.store.append_event(
            session_id,
            "lesson-v1",
            "flashcard.attempted",
            "diagnose",
            {"concept_id": "CON-PT-001", "trace_kind": "retrieval_practice", "revealed": True},
            provenance,
        )
        self.store.append_event(
            session_id,
            "lesson-v1",
            "overlay.updated",
            "diagnose",
            {"overlay": {"title": "Tensor exploration", "concept_ids": ["CON-PT-001"], "package_version": package_version}},
            provenance,
        )
        snapshot = self.store.snapshot(session_id, "lesson-v1")
        restarted = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)
        replayed = restarted.snapshot(session_id, "lesson-v1")
        self.assertEqual(snapshot["state"], replayed["state"])
        self.assertEqual(replayed["state"]["phase"], "diagnose")
        self.assertEqual(len(replayed["state"]["study_traces"]), 2)
        self.assertEqual(replayed["state"]["evidence"], [])
        self.assertEqual(replayed["state"]["overlay"]["concept_ids"], ["CON-PT-001"])
        self.assertTrue(all(event["package_version"] == package_version for event in replayed["events"]))

    def test_structured_observation_replays_with_evaluator_provenance(self) -> None:
        session_id = "structured-evidence-test"
        provenance = {
            "package_version": "0.1.0",
            "actor": "grader-api",
            "evaluator": {
                "type": "deterministic",
                "evaluator_id": "rubric-pt-g3-gradient-accumulation",
                "evaluator_version": 1,
            },
        }
        observation = {
            "schema": "learning-evidence/v1",
            "activity_id": "diagnostic.gradient-accumulation.baseline",
            "label": "gradient_accumulation",
            "status": "abstained",
            "result": "abstain",
            "evidence_spans": [],
            "alternatives": ["stale_gradient_accumulation"],
            "evaluator": provenance["evaluator"],
            "failure_type": "knowledge_gap",
        }
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {}, provenance)
        first = self.store.append_event(
            session_id,
            "lesson-v1",
            "diagnostic.submitted",
            "diagnose",
            {"observation": observation},
            provenance,
        )
        restarted = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)
        replayed = restarted.snapshot(session_id, "lesson-v1")
        self.assertEqual(replayed["state"]["evidence"], [observation])
        self.assertEqual(first["events"][-1]["evaluator"], provenance["evaluator"])
        self.assertEqual(replayed["events"][-1]["evaluator"], provenance["evaluator"])


    def test_tutor_chat_and_proposals_replay_without_affecting_mastery(self) -> None:
        session_id = "tutor-test"
        proposal = {
            "schema": "learning-evidence/v1",
            "label": "stale_gradient_accumulation",
            "status": "candidate",
            "result": "advisory",
            "advisory": True,
            "confidence_source": {
                "type": "model",
                "evaluator_id": "model-tutor-pt-g4",
                "model": "claude-opus-5-5",
                "prompt_version": "tutor-pt-g4-v1",
            },
            "evidence_spans": ["backward replaces the gradients"],
            "alternatives": ["gradient_accumulation"],
        }
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {})
        self.store.append_event(
            session_id, "lesson-v1", "chat.learner", "diagnose",
            {"role": "learner", "text": "The loss flattens after a few steps."},
            {"actor": "learner-ui"},
        )
        self.store.append_event(
            session_id, "lesson-v1", "chat.tutor", "diagnose",
            {"role": "tutor", "text": "What happens to .grad before backward?", "source": "model"},
            {"actor": "model-tutor"},
        )
        self.store.append_event(
            session_id, "lesson-v1", "tutor.observation.proposed", "diagnose",
            {"observation": proposal},
            {"actor": "model-tutor", "evaluator": proposal["confidence_source"]},
        )

        # Pure replay from a fresh store reconstructs the thread with no model call.
        restarted = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)
        state = restarted.snapshot(session_id, "lesson-v1")["state"]
        self.assertEqual([m["type"] for m in state["thread"]], ["chat.learner", "chat.tutor"])
        self.assertEqual(state["thread"][1]["text"], "What happens to .grad before backward?")
        self.assertEqual(state["tutor_proposals"], [proposal])
        # The advisory proposal must not become mastery evidence or move the phase.
        self.assertEqual(state["evidence"], [])
        self.assertEqual(state["phase"], "diagnose")

    def test_chat_is_legal_in_every_phase(self) -> None:
        session_id = "chat-phase-test"
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {})
        self.store.append_event(session_id, "lesson-v1", "diagnostic.submitted", "diagnose", {})
        # Now in the teach phase; a chat event here must be accepted.
        result = self.store.append_event(
            session_id, "lesson-v1", "chat.tutor", "teach",
            {"role": "tutor", "text": "Restate it back to me."}, {"actor": "scripted-tutor"},
        )
        self.assertEqual(result["state"]["phase"], "teach")
        self.assertEqual(len(result["state"]["thread"]), 1)

    def test_disambiguation_request_replays_without_affecting_evidence(self) -> None:
        session_id = "disambiguation-test"
        request = {
            "schema": "learning-disambiguation/v1",
            "reason": "evaluator_conflict",
            "source": {"type": "derived", "evaluator_id": "tutor-conflict-g4-v1", "evaluator_version": 1},
            "item": {"id": "disambiguator.gradient-accumulation.double-backward", "prompt": "Trace two backward passes."},
        }
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {})
        self.store.append_event(
            session_id,
            "lesson-v1",
            "tutor.disambiguation.requested",
            "diagnose",
            request,
            {"actor": "learning-controller", "evaluator": request["source"]},
        )
        first = self.store.snapshot(session_id, "lesson-v1")
        restarted = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)
        second = restarted.snapshot(session_id, "lesson-v1")
        self.assertEqual(first["state"], second["state"])
        self.assertEqual(second["state"]["disambiguation_requests"], [request])
        self.assertEqual(second["state"]["evidence"], [])
        self.assertEqual(second["state"]["phase"], "diagnose")

    def test_agent_trace_replays_without_becoming_evidence(self) -> None:
        session_id = "agent-trace-test"
        trace = {
            "schema": "learning-agent-trace/v1",
            "runtime": "messages-loop",
            "model": "fixture-model",
            "sdk_version": "fixture",
            "prompt_version": "agent-tutor-g45-v1",
            "events": [
                {"sequence": 1, "type": "tool.call", "data": {"name": "get_concept"}},
                {"sequence": 2, "type": "agent.response", "data": {"result": {"reply": "Trace it."}}},
            ],
        }
        self.store.append_event(session_id, "lesson-v1", "session.started", "diagnose", {})
        self.store.append_event(
            session_id,
            "lesson-v1",
            "agent.trace.recorded",
            "diagnose",
            {"trace": trace},
            {"actor": "agent-runtime", "evaluator": {"type": "runtime", "runtime": "messages-loop"}},
        )
        restarted = SessionStore(Path(self.tempdir.name) / "session.sqlite3", PHASES)
        state = restarted.snapshot(session_id, "lesson-v1")["state"]
        self.assertEqual(state["agent_traces"], [trace])
        self.assertEqual(state["evidence"], [])
        self.assertEqual(state["phase"], "diagnose")


if __name__ == "__main__":
    unittest.main()
