#!/usr/bin/env python3
"""Offline tests for the G4.5 agent-runtime primitives lab."""

from __future__ import annotations

import json
import sys
import unittest
from types import SimpleNamespace

import agent_runtime


LESSON = {
    "subject": "PyTorch foundations",
    "objective": "Explain gradient accumulation.",
    "package_version": "0.1.0",
    "concepts": {
        "CON-PT-003": {
            "name": "Backward and gradient accumulation",
            "summary": "backward adds to .grad until a reset defines a new window",
        }
    },
    "activities": {
        "diagnostic.gradient-accumulation.baseline": {"kind": "open_response"},
    },
    "diagnostic": {
        "disambiguator": {
            "id": "disambiguator.gradient-accumulation.double-backward",
            "prompt": "Trace two backward passes.",
        }
    },
}


class Block:
    def __init__(self, block_type: str, **fields: object) -> None:
        self.type = block_type
        for key, value in fields.items():
            setattr(self, key, value)

    def model_dump(self, *, mode: str = "json") -> dict[str, object]:
        return {key: value for key, value in self.__dict__.items() if key != "type"} | {"type": self.type}


class FakeMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.responses = [
            SimpleNamespace(content=[Block("tool_use", id="tool-1", name="get_concept", input={"concept_id": "CON-PT-003"})]),
            SimpleNamespace(content=[Block("text", text=json.dumps({
                "reply": "What happens to .grad after a second backward?",
                "proposed_observation": {"status": "none", "label": "", "evidence_spans": [], "alternatives": [], "rationale": ""},
                "suggested_next": "Trace two passes.",
            }))]),
        ]

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return self.responses.pop(0)


class FakeClient:
    def __init__(self) -> None:
        self.messages = FakeMessages()


class MessagesAgentPortTests(unittest.TestCase):
    def test_direct_loop_executes_allow_listed_tool_and_replays(self) -> None:
        result = agent_runtime.MessagesAgentPort(FakeClient()).run(
            learner_message="I am unsure.", history=[], lesson=LESSON, session_state={"phase": "diagnose"}
        )
        self.assertEqual(result["runtime"], "messages-loop")
        self.assertEqual(result["source"], "agent")
        self.assertEqual(result["reply"], "What happens to .grad after a second backward?")
        trace = result["trace"]
        self.assertEqual(trace["schema"], "learning-agent-trace/v1")
        replayed = agent_runtime.replay_trace(trace)
        self.assertEqual(replayed["reply"], result["reply"])
        self.assertNotIn("trace", replayed)
        self.assertEqual(
            [event["type"] for event in trace["events"]],
            ["agent.message", "tool.call", "tool.result", "agent.message", "agent.response"],
        )
        json.dumps(trace)

    def test_registry_rejects_unknown_or_extra_arguments(self) -> None:
        registry = agent_runtime.ToolRegistry.for_lesson(LESSON)
        with self.assertRaises(agent_runtime.AgentRuntimeError):
            registry.execute("write_mastery", {})
        with self.assertRaises(agent_runtime.AgentRuntimeError):
            registry.execute("get_concept", {"concept_id": "CON-PT-003", "write": True})


class ToolRunnerAdapterTests(unittest.TestCase):
    def test_tool_runner_adapter_executes_allow_listed_tool_without_network(self) -> None:
        try:
            import anthropic
        except ImportError as error:  # pragma: no cover - dependency is locked
            self.skipTest(str(error))
        self.assertTrue(hasattr(anthropic, "beta_tool"))

        class FakeRunner:
            def __init__(self, tools: list[object]) -> None:
                self.tools = tools

            def until_done(self) -> SimpleNamespace:
                self.tools[0].call({"concept_id": "CON-PT-003"})
                return SimpleNamespace(content=[Block("text", text=json.dumps({
                    "reply": "The tool returned the authored concept.",
                    "proposed_observation": {"status": "none", "label": "", "evidence_spans": [], "alternatives": [], "rationale": ""},
                    "suggested_next": "Trace two passes.",
                }))])

        class FakeToolRunnerMessages:
            def tool_runner(self, **kwargs: object) -> FakeRunner:
                return FakeRunner(kwargs["tools"])

        fake_client = SimpleNamespace(beta=SimpleNamespace(messages=FakeToolRunnerMessages()))
        result = agent_runtime.ToolRunnerAgentPort(fake_client).run(
            learner_message="Explain accumulation.", history=[], lesson=LESSON, session_state={"phase": "diagnose"}
        )
        self.assertEqual(result["runtime"], "anthropic-tool-runner")
        self.assertEqual(result["reply"], "The tool returned the authored concept.")
        self.assertEqual([event["type"] for event in result["trace"]["events"]], ["tool.call", "tool.result", "agent.message", "agent.response"])


if __name__ == "__main__":
    sys.path.insert(0, ".")
    unittest.main()
