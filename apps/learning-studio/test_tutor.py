#!/usr/bin/env python3
"""Tests for the advisory model tutor: scripted fallback and model-path parsing.

No test makes a live API call — the Anthropic client is mocked so the structured
output parsing and the advisory-proposal mapping are exercised deterministically.
"""

from __future__ import annotations

import contextlib
import json
import unittest
from unittest import mock

import tutor

LESSON = {
    "subject": "PyTorch foundations",
    "objective": "Explain why gradients are cleared before backprop.",
    "phases": ["diagnose", "teach", "practice", "verify", "review"],
    "package_version": "0.1.0",
}


class _Block:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Response:
    def __init__(self, text: str) -> None:
        self.content = [_Block(text)]


class _FakeClient:
    """Minimal stand-in for anthropic.Anthropic returning a canned JSON response."""

    def __init__(self, payload_text: str) -> None:
        self._payload_text = payload_text

    def with_options(self, **_kwargs: object) -> "_FakeClient":
        return self

    @property
    def messages(self) -> "_FakeClient":
        return self

    def create(self, **_kwargs: object) -> _Response:
        return _Response(self._payload_text)


@contextlib.contextmanager
def _fake_anthropic(payload_text: str):
    # Model-path tests force availability on and supply a canned client.
    with mock.patch.object(tutor, "tutor_available", return_value=True), \
            mock.patch("anthropic.Anthropic", return_value=_FakeClient(payload_text)):
        yield


class ScriptedTutorTests(unittest.TestCase):
    def test_scripted_turn_is_phase_aware(self) -> None:
        turn = tutor.scripted_turn({"phase": "practice"}, "I'm not sure", LESSON)
        self.assertEqual(turn["source"], "scripted")
        self.assertIsNone(turn["proposed_observation"])
        self.assertIn("resets the accumulated gradients", turn["reply"])

    def test_falls_back_without_credential(self) -> None:
        with mock.patch.object(tutor, "tutor_available", return_value=False):
            turn = tutor.generate_tutor_turn(
                lesson=LESSON, session_state={"phase": "diagnose"}, history=[], learner_message="hi",
            )
        self.assertEqual(turn["source"], "scripted")
        self.assertEqual(turn["fallback_reason"], "no_credential")

    def test_falls_back_when_client_build_fails(self) -> None:
        with mock.patch.object(tutor, "tutor_available", return_value=True), \
                mock.patch("anthropic.Anthropic", side_effect=RuntimeError("boom")):
            turn = tutor.generate_tutor_turn(
                lesson=LESSON, session_state={"phase": "diagnose"}, history=[], learner_message="hi",
            )
        self.assertEqual(turn["source"], "scripted")
        self.assertEqual(turn["fallback_reason"], "no_client")


class ModelTutorTests(unittest.TestCase):
    def test_abstention_requests_disambiguator_without_evidence(self) -> None:
        proposal = {
            "label": "gradient_accumulation",
            "status": "abstained",
            "advisory": True,
        }
        request = tutor.build_disambiguation_request(
            proposal,
            {"label": "gradient_accumulation", "status": "abstained"},
            phase="diagnose",
            item={"id": "disambiguator.test", "prompt": "Trace two backward passes."},
        )
        self.assertIsNotNone(request)
        self.assertEqual(request["reason"], "model_abstained")
        self.assertEqual(request["schema"], "learning-disambiguation/v1")
        self.assertEqual(request["item"]["id"], "disambiguator.test")

    def test_matching_candidate_does_not_request_disambiguator(self) -> None:
        request = tutor.build_disambiguation_request(
            {"label": "gradient_accumulation", "status": "candidate"},
            {"label": "gradient_accumulation", "status": "supported"},
            phase="diagnose",
            item={"id": "disambiguator.test", "prompt": "Trace two backward passes."},
        )
        self.assertIsNone(request)

    def test_conflicting_candidate_requests_disambiguator(self) -> None:
        request = tutor.build_disambiguation_request(
            {"label": "stale_gradient_accumulation", "status": "candidate"},
            {"label": "gradient_accumulation", "status": "supported"},
            phase="diagnose",
            item={"id": "disambiguator.test", "prompt": "Trace two backward passes."},
        )
        self.assertIsNotNone(request)
        self.assertEqual(request["reason"], "evaluator_conflict")

    def test_model_json_is_parsed_and_proposal_is_advisory(self) -> None:
        payload = json.dumps({
            "reply": "What happens to .grad right after backward?",
            "proposed_observation": {
                "status": "candidate",
                "label": "stale_gradient_accumulation",
                "evidence_spans": ["backward replaces the gradients"],
                "alternatives": ["gradient_accumulation"],
                "rationale": "The learner thinks backward overwrites .grad.",
            },
            "suggested_next": "Ask them to trace one batch.",
        })
        with _fake_anthropic(payload):
            turn = tutor.generate_tutor_turn(
                lesson=LESSON, session_state={"phase": "diagnose"}, history=[],
                learner_message="backward replaces the gradients each step",
            )
        self.assertEqual(turn["source"], "model")
        self.assertEqual(turn["reply"], "What happens to .grad right after backward?")
        prop = turn["proposed_observation"]
        self.assertIsNotNone(prop)
        # Advisory, model-sourced, and explicitly not a gradeable result.
        self.assertTrue(prop["advisory"])
        self.assertEqual(prop["result"], "advisory")
        self.assertEqual(prop["status"], "candidate")
        self.assertEqual(prop["label"], "stale_gradient_accumulation")
        self.assertEqual(prop["confidence_source"]["type"], "model")
        self.assertIn("backward replaces the gradients", prop["evidence_spans"])

    def test_status_none_yields_no_proposal(self) -> None:
        payload = json.dumps({
            "reply": "Tell me more.",
            "proposed_observation": {
                "status": "none", "label": "", "evidence_spans": [],
                "alternatives": [], "rationale": "",
            },
            "suggested_next": "",
        })
        with _fake_anthropic(payload):
            turn = tutor.generate_tutor_turn(
                lesson=LESSON, session_state={"phase": "diagnose"}, history=[], learner_message="ok",
            )
        self.assertEqual(turn["source"], "model")
        self.assertIsNone(turn["proposed_observation"])

    def test_unparseable_model_output_falls_back_to_scripted(self) -> None:
        with _fake_anthropic("not json at all"):
            turn = tutor.generate_tutor_turn(
                lesson=LESSON, session_state={"phase": "review"}, history=[], learner_message="ok",
            )
        self.assertEqual(turn["source"], "scripted")
        self.assertTrue(turn["fallback_reason"].startswith("api_error:"))


if __name__ == "__main__":
    unittest.main()
