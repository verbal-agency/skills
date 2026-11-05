#!/usr/bin/env python3
"""Run the offline G4.5 direct-loop fixture and replay its trace."""

from __future__ import annotations

import json
from types import SimpleNamespace

from agent_runtime import MessagesAgentPort, replay_trace


class Block:
    def __init__(self, block_type: str, **fields: object) -> None:
        self.type = block_type
        self.__dict__.update(fields)

    def model_dump(self, *, mode: str = "json") -> dict[str, object]:
        return {key: value for key, value in self.__dict__.items() if key != "type"} | {"type": self.type}


class FixtureMessages:
    def __init__(self) -> None:
        self.responses = [
            SimpleNamespace(content=[Block("tool_use", id="tool-1", name="get_concept", input={"concept_id": "CON-PT-003"})]),
            SimpleNamespace(content=[Block("text", text=json.dumps({
                "reply": "What happens to .grad after a second backward?",
                "proposed_observation": {"status": "none", "label": "", "evidence_spans": [], "alternatives": [], "rationale": ""},
                "suggested_next": "Trace two passes.",
            }))]),
        ]

    def create(self, **kwargs: object) -> SimpleNamespace:
        return self.responses.pop(0)


class FixtureClient:
    def __init__(self) -> None:
        self.messages = FixtureMessages()


LESSON = {
    "subject": "PyTorch foundations",
    "objective": "Explain gradient accumulation.",
    "concepts": {"CON-PT-003": {"name": "Backward and gradient accumulation"}},
    "activities": {"diagnostic.gradient-accumulation.baseline": {"kind": "open_response"}},
    "diagnostic": {"disambiguator": {"id": "disambiguator.gradient-accumulation.double-backward", "prompt": "Trace two backward passes."}},
}


def main() -> None:
    result = MessagesAgentPort(FixtureClient()).run(
        learner_message="I am unsure.", history=[], lesson=LESSON, session_state={"phase": "diagnose"}
    )
    print(json.dumps({
        "runtime": result["runtime"],
        "reply": result["reply"],
        "trace_events": [event["type"] for event in result["trace"]["events"]],
        "replayed_reply": replay_trace(result["trace"])["reply"],
    }, indent=2))


if __name__ == "__main__":
    main()
