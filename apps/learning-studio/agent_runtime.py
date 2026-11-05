"""Bounded agent-runtime primitives for roadmap goal G4.5.

This module keeps the learning-studio controller in charge of authority while
making the agent loop replaceable. The direct Messages loop is the baseline;
the Anthropic tool-runner adapter is optional and imported only when selected.
Neither runtime writes SQLite or learner state. They return a structured tutor
result plus a replayable trace for the controller to record.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from tutor import PROMPT_VERSION, TUTOR_MODEL, TUTOR_SCHEMA


AGENT_TRACE_SCHEMA = "learning-agent-trace/v1"
AGENT_PROMPT_VERSION = "agent-tutor-g45-v1"


class AgentRuntimeError(RuntimeError):
    """Raised when an agent response or tool call violates the local contract."""


class AgentPort(Protocol):
    """Provider-neutral boundary used by the tutor controller."""

    runtime_name: str

    def run(
        self,
        *,
        learner_message: str,
        history: list[dict[str, Any]],
        lesson: dict[str, Any],
        session_state: dict[str, Any],
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]


class ToolRegistry:
    """Typed, allow-listed tools that cannot access persistence directly."""

    def __init__(self, tools: list[ToolSpec]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    @classmethod
    def for_lesson(cls, lesson: dict[str, Any]) -> "ToolRegistry":
        concepts = lesson.get("concepts", {})
        activities = lesson.get("activities", {})
        disambiguator = lesson.get("diagnostic", {}).get("disambiguator", {})

        def get_concept(arguments: dict[str, Any]) -> dict[str, Any]:
            concept_id = arguments["concept_id"]
            concept = concepts.get(concept_id)
            if concept is None:
                raise AgentRuntimeError(f"unknown concept: {concept_id}")
            return {"concept_id": concept_id, "concept": concept}

        def ask_disambiguating_question(arguments: dict[str, Any]) -> dict[str, Any]:
            item_id = arguments["item_id"]
            if item_id != disambiguator.get("id"):
                raise AgentRuntimeError(f"unknown disambiguator: {item_id}")
            return {"item": disambiguator}

        def propose_next_activity(arguments: dict[str, Any]) -> dict[str, Any]:
            activity_id = arguments["activity_id"]
            activity = activities.get(activity_id)
            if activity is None:
                raise AgentRuntimeError(f"unknown activity: {activity_id}")
            return {"activity_id": activity_id, "activity": activity, "advisory": True}

        return cls([
            ToolSpec(
                name="get_concept",
                description="Retrieve an authored concept by ID. This is read-only.",
                input_schema={
                    "type": "object",
                    "properties": {"concept_id": {"type": "string"}},
                    "required": ["concept_id"],
                    "additionalProperties": False,
                },
                handler=get_concept,
            ),
            ToolSpec(
                name="ask_disambiguating_question",
                description="Retrieve an authored clarifying item. This does not grade the learner.",
                input_schema={
                    "type": "object",
                    "properties": {"item_id": {"type": "string"}},
                    "required": ["item_id"],
                    "additionalProperties": False,
                },
                handler=ask_disambiguating_question,
            ),
            ToolSpec(
                name="propose_next_activity",
                description="Propose an authored next activity without changing session state.",
                input_schema={
                    "type": "object",
                    "properties": {"activity_id": {"type": "string"}},
                    "required": ["activity_id"],
                    "additionalProperties": False,
                },
                handler=propose_next_activity,
            ),
        ])

    def definition_list(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    def execute(self, name: str, arguments: Any) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            raise AgentRuntimeError(f"tool is not allow-listed: {name}")
        if not isinstance(arguments, dict):
            raise AgentRuntimeError(f"tool arguments must be an object: {name}")
        required = tool.input_schema.get("required", [])
        properties = tool.input_schema.get("properties", {})
        missing = [key for key in required if key not in arguments]
        extra = [key for key in arguments if key not in properties]
        if missing or extra:
            raise AgentRuntimeError(f"invalid arguments for {name}: missing={missing}, extra={extra}")
        return tool.handler(arguments)


class TraceRecorder:
    def __init__(self, runtime: str, model: str, sdk_version: str) -> None:
        self.runtime = runtime
        self.model = model
        self.sdk_version = sdk_version
        self.events: list[dict[str, Any]] = []

    def add(self, event_type: str, data: dict[str, Any]) -> None:
        self.events.append({
            "sequence": len(self.events) + 1,
            "type": event_type,
            "runtime": self.runtime,
            "model": self.model,
            "sdk_version": self.sdk_version,
            "prompt_version": AGENT_PROMPT_VERSION,
            "data": data,
        })

    def finish(self, result: dict[str, Any]) -> dict[str, Any]:
        self.add("agent.response", {"result": {key: value for key, value in result.items() if key != "trace"}})
        return {
            "schema": AGENT_TRACE_SCHEMA,
            "runtime": self.runtime,
            "model": self.model,
            "sdk_version": self.sdk_version,
            "prompt_version": AGENT_PROMPT_VERSION,
            "events": self.events,
        }


def replay_trace(trace: dict[str, Any]) -> dict[str, Any]:
    """Recover the final result from recorded events without a model call."""

    if trace.get("schema") != AGENT_TRACE_SCHEMA:
        raise AgentRuntimeError("unsupported agent trace schema")
    responses = [event for event in trace.get("events", []) if event.get("type") == "agent.response"]
    if len(responses) != 1:
        raise AgentRuntimeError("agent trace must contain exactly one final response")
    return responses[0]["data"]["result"]


def _system_prompt(lesson: dict[str, Any], session_state: dict[str, Any]) -> str:
    return (
        f"You are a bounded tutor for {lesson.get('subject', 'this subject')}. "
        f"The current phase is {session_state.get('phase', 'diagnose')}. "
        "Use tools only to retrieve authored context or make advisory proposals. "
        "Never claim that a tool call changes mastery. Return JSON matching the tutor schema."
    )


def _messages(history: list[dict[str, Any]], learner_message: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for entry in history[-10:]:
        role = "assistant" if entry.get("type") == "chat.tutor" else "user"
        text = str(entry.get("text", "")).strip()
        if text:
            messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": learner_message})
    return messages


def _parse_final(content: list[Any]) -> dict[str, Any]:
    text_blocks = [getattr(block, "text", "") for block in content if getattr(block, "type", None) == "text"]
    if not text_blocks:
        raise AgentRuntimeError("agent returned no final text")
    try:
        result = json.loads(text_blocks[-1])
    except json.JSONDecodeError as error:
        raise AgentRuntimeError("agent final response was not JSON") from error
    if not isinstance(result, dict) or not isinstance(result.get("reply"), str):
        raise AgentRuntimeError("agent final response violated tutor contract")
    return result


def _trace_content(content: list[Any]) -> list[Any]:
    """Convert SDK content blocks into JSON-safe trace data."""

    serialized: list[Any] = []
    for block in content:
        if hasattr(block, "model_dump"):
            serialized.append(block.model_dump(mode="json"))
        elif isinstance(block, dict):
            serialized.append(block)
        else:
            serialized.append({
                "type": getattr(block, "type", "unknown"),
                "text": getattr(block, "text", None),
                "name": getattr(block, "name", None),
                "id": getattr(block, "id", None),
                "input": getattr(block, "input", None),
            })
    return serialized


class MessagesAgentPort:
    """Manual tool loop baseline with explicit trace and controller validation."""

    runtime_name = "messages-loop"

    def __init__(self, client: Any, *, model: str = TUTOR_MODEL, max_iterations: int = 4, sdk_version: str = "anthropic-messages") -> None:
        self.client = client
        self.model = model
        self.max_iterations = max_iterations
        self.sdk_version = sdk_version

    def run(self, *, learner_message: str, history: list[dict[str, Any]], lesson: dict[str, Any], session_state: dict[str, Any]) -> dict[str, Any]:
        registry = ToolRegistry.for_lesson(lesson)
        recorder = TraceRecorder(self.runtime_name, self.model, self.sdk_version)
        messages = _messages(history, learner_message)
        for iteration in range(self.max_iterations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                system=_system_prompt(lesson, session_state),
                tools=registry.definition_list(),
                messages=messages,
                output_config={"format": {"type": "json_schema", "schema": TUTOR_SCHEMA}},
            )
            recorder.add("agent.message", {"iteration": iteration, "content": _trace_content(response.content)})
            tool_uses = [block for block in response.content if getattr(block, "type", None) == "tool_use"]
            if not tool_uses:
                result = _parse_final(response.content)
                result.update({"source": "agent", "runtime": self.runtime_name, "model": self.model, "prompt_version": AGENT_PROMPT_VERSION})
                result["trace"] = recorder.finish(result)
                return result
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in tool_uses:
                name = str(block.name)
                arguments = block.input if isinstance(block.input, dict) else {}
                recorder.add("tool.call", {"iteration": iteration, "name": name, "arguments": arguments})
                try:
                    value = registry.execute(name, arguments)
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(value, sort_keys=True)})
                    recorder.add("tool.result", {"name": name, "ok": True, "value": value})
                except AgentRuntimeError as error:
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "is_error": True, "content": str(error)})
                    recorder.add("tool.result", {"name": name, "ok": False, "error": str(error)})
            messages.append({"role": "user", "content": tool_results})
        raise AgentRuntimeError(f"agent exceeded max_iterations={self.max_iterations}")


class ToolRunnerAgentPort:
    """Optional Anthropic Python tool-runner adapter.

    This is deliberately separate from the controller. The SDK executes the
    allow-listed functions; the resulting message is still only a proposal.
    """

    runtime_name = "anthropic-tool-runner"

    def __init__(self, client: Any, *, model: str = TUTOR_MODEL, max_iterations: int = 4, sdk_version: str = "anthropic-tool-runner") -> None:
        self.client = client
        self.model = model
        self.max_iterations = max_iterations
        self.sdk_version = sdk_version

    def run(self, *, learner_message: str, history: list[dict[str, Any]], lesson: dict[str, Any], session_state: dict[str, Any]) -> dict[str, Any]:
        try:
            from anthropic import beta_tool
        except Exception as error:
            raise AgentRuntimeError("Anthropic beta tool runner is unavailable") from error
        registry = ToolRegistry.for_lesson(lesson)
        recorder = TraceRecorder(self.runtime_name, self.model, self.sdk_version)
        wrapped_tools = []
        for spec in registry._tools.values():
            def make_tool(current: ToolSpec) -> Any:
                def invoke(arguments: dict[str, Any]) -> str:
                    recorder.add("tool.call", {"name": current.name, "arguments": arguments})
                    try:
                        value = registry.execute(current.name, arguments)
                    except AgentRuntimeError as error:
                        recorder.add("tool.result", {"name": current.name, "ok": False, "error": str(error)})
                        raise
                    recorder.add("tool.result", {"name": current.name, "ok": True, "value": value})
                    return json.dumps(value, sort_keys=True)

                if current.name == "get_concept":
                    @beta_tool
                    def get_concept(concept_id: str) -> str:
                        """Retrieve an authored concept by ID."""
                        return invoke({"concept_id": concept_id})
                    return get_concept
                if current.name == "ask_disambiguating_question":
                    @beta_tool
                    def ask_disambiguating_question(item_id: str) -> str:
                        """Retrieve an authored clarifying item by ID."""
                        return invoke({"item_id": item_id})
                    return ask_disambiguating_question
                @beta_tool
                def propose_next_activity(activity_id: str) -> str:
                    """Propose an authored next activity by ID."""
                    return invoke({"activity_id": activity_id})
                return propose_next_activity
            wrapped_tools.append(make_tool(spec))
        runner = self.client.beta.messages.tool_runner(
            model=self.model,
            max_tokens=1200,
            max_iterations=self.max_iterations,
            tools=wrapped_tools,
            system=_system_prompt(lesson, session_state),
            messages=_messages(history, learner_message),
            output_config={"format": {"type": "json_schema", "schema": TUTOR_SCHEMA}},
        )
        final = runner.until_done()
        recorder.add("agent.message", {"content": _trace_content(final.content)})
        result = _parse_final(final.content)
        result.update({"source": "agent", "runtime": self.runtime_name, "model": self.model, "prompt_version": AGENT_PROMPT_VERSION})
        result["trace"] = recorder.finish(result)
        return result
