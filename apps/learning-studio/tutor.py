"""Optional model-assisted tutor for the Learning Studio (roadmap G4, advisory).

The tutor holds a Socratic conversation beside the deterministic session. It may
*propose* a diagnosis observation, but the proposal is advisory only: it is
recorded as a `tutor.observation.proposed` event and never enters `evidence`, so
it cannot move mastery or advance a phase. The deterministic grader in
`grading.py` remains the only evaluator that affects learner state.

The `anthropic` SDK is imported lazily and every model call is wrapped so that a
missing credential, a missing dependency, or any API error degrades to a
scripted, phase-aware reply. This keeps the app usable with no API key.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from grading import EVIDENCE_SCHEMA

DEFAULT_TUTOR_MODEL = "claude-opus-5-5"
TUTOR_MODEL = os.environ.get("LEARNING_STUDIO_TUTOR_MODEL", DEFAULT_TUTOR_MODEL)
PROMPT_VERSION = "tutor-pt-g4-v1"
EVALUATOR_ID = "model-tutor-pt-g4"

# Structured-output contract. `proposed_observation.status == "none"` means the
# tutor saw no gradeable signal in the learner's message — the common case.
TUTOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "proposed_observation": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["candidate", "abstained", "none"]},
                "label": {"type": "string"},
                "evidence_spans": {"type": "array", "items": {"type": "string"}},
                "alternatives": {"type": "array", "items": {"type": "string"}},
                "rationale": {"type": "string"},
            },
            "required": ["status", "label", "evidence_spans", "alternatives", "rationale"],
            "additionalProperties": False,
        },
        "suggested_next": {"type": "string"},
    },
    "required": ["reply", "proposed_observation", "suggested_next"],
    "additionalProperties": False,
}

_SYSTEM_TEMPLATE = """You are the tutor in a learning studio, teaching "{subject}".

Lesson objective: {objective}
Current phase: {phase} (of diagnose -> teach -> practice -> verify -> review)

Your job is to help the learner reason, not to hand them the answer. Be Socratic
and brief: 2-4 sentences, plain language, one idea at a time. During the diagnose
and practice phases especially, do NOT state the correct fix outright — ask a
question that makes the mechanism observable.

You may propose a diagnosis observation about the learner's current message, but
only as an advisory signal: it never decides mastery. Set
proposed_observation.status to:
- "candidate" when the message shows a specific, nameable understanding or
  misconception (put the exact phrases that justify it in evidence_spans);
- "abstained" when there is a hint but not enough to distinguish causes;
- "none" when the message carries no gradeable signal (questions, small talk,
  "I don't know"). This is the default — prefer it when unsure.
Never invent evidence_spans; quote only what the learner actually wrote.

For this PyTorch lesson the target mechanism is gradient accumulation: gradients
add into each parameter's .grad buffer, and optimizer.zero_grad() clears them so
each step uses only the current batch."""


def tutor_available() -> bool:
    """True when a live tutor is likely usable (SDK present and a credential resolvable).

    This only decides the UI label ("AI tutor" vs "Guided tutor"); the actual call
    path falls back to a scripted reply on any failure, so a false positive here is
    harmless.
    """

    try:
        import anthropic  # noqa: F401
    except Exception:
        return False
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    # An `ant auth login` profile also authenticates the zero-argument client.
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config_home) if config_home else Path.home() / ".config"
    return (base / "anthropic").exists()


_SCRIPTED_BY_PHASE = {
    "diagnose": "Before I explain anything: what do you think happens to a parameter's "
    ".grad value right after loss.backward()? Say it in your own words, even if you're unsure.",
    "teach": "Good — now restate it back to me: why does optimizer.zero_grad() have to run "
    "before the next batch's backward pass, and not after?",
    "practice": "Look at the loop and ask yourself which single operation resets the "
    "accumulated gradients. Which line would you add, and where?",
    "verify": "The repair passed the check. Can you tell me what that does NOT yet prove about "
    "whether you've really mastered this?",
    "review": "New prompt, same idea: predict what happens to the updates if gradients are "
    "never cleared across batches, and name the mechanism behind it.",
}


def scripted_turn(session_state: dict[str, Any], learner_message: str, lesson: dict[str, Any], *, reason: str = "no_credential") -> dict[str, Any]:
    """Phase-aware fallback reply used whenever the live tutor is unavailable."""

    phase = session_state.get("phase", lesson.get("phases", ["diagnose"])[0])
    reply = _SCRIPTED_BY_PHASE.get(phase, "Tell me more about your thinking so I can help.")
    return {
        "reply": reply,
        "proposed_observation": None,
        "source": "scripted",
        "model": None,
        "prompt_version": PROMPT_VERSION,
        "fallback_reason": reason,
    }


def _system_prompt(lesson: dict[str, Any], session_state: dict[str, Any]) -> str:
    return _SYSTEM_TEMPLATE.format(
        subject=lesson.get("subject", "this subject"),
        objective=lesson.get("objective", ""),
        phase=session_state.get("phase", "diagnose"),
    )


def _history_to_messages(history: list[dict[str, Any]], limit: int = 10) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for entry in history[-limit:]:
        role = "assistant" if entry.get("type") == "chat.tutor" else "user"
        text = str(entry.get("text", "")).strip()
        if text:
            messages.append({"role": role, "content": text})
    return messages


def _build_proposal(raw: Any, model: str) -> dict[str, Any] | None:
    """Convert the model's proposed_observation into an advisory evidence-shaped record.

    Returns None for the common "none" case. The record mirrors the deterministic
    grader's shape (so the UI can render it) but is tagged advisory and carries a
    model confidence source — it is never deterministic evidence.
    """

    if not isinstance(raw, dict):
        return None
    status = str(raw.get("status", "none"))
    if status not in {"candidate", "abstained"}:
        return None
    label = str(raw.get("label", "unlabeled")).strip() or "unlabeled"
    spans = [str(s) for s in raw.get("evidence_spans", []) if isinstance(s, str)]
    alternatives = [str(a) for a in raw.get("alternatives", []) if isinstance(a, str)]
    rationale = str(raw.get("rationale", "")).strip()
    return {
        "schema": EVIDENCE_SCHEMA,
        "label": label,
        "status": status,
        # "advisory" is deliberately not one of the grader's results; it signals
        # the UI and replay that this never counts as mastery evidence.
        "result": "advisory",
        "failure_type": None,
        "evidence_spans": spans,
        "alternatives": alternatives,
        "confidence_source": {
            "type": "model",
            "evaluator_id": EVALUATOR_ID,
            "model": model,
            "prompt_version": PROMPT_VERSION,
        },
        "evidence_refs": [],
        "advisory": True,
        "kind": "neutral",
        "title": f"Proposed: {label.replace('_', ' ')} ({status})",
        "detail": rationale or "Advisory model proposal — not mastery evidence.",
    }


def generate_tutor_turn(
    *,
    lesson: dict[str, Any],
    session_state: dict[str, Any],
    history: list[dict[str, Any]],
    learner_message: str,
    model: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Produce one tutor turn, degrading to a scripted reply on any failure."""

    model = model or TUTOR_MODEL
    # Short-circuit the common no-credential case to a scripted reply, so the
    # backend matches the UI's "Guided tutor" label and we never build a client
    # with no key (which the SDK fails on with an opaque error).
    if not tutor_available():
        return scripted_turn(session_state, learner_message, lesson, reason="no_credential")
    try:
        import anthropic
    except Exception:
        return scripted_turn(session_state, learner_message, lesson, reason="sdk_missing")

    try:
        client = anthropic.Anthropic()
    except Exception:
        return scripted_turn(session_state, learner_message, lesson, reason="no_client")

    messages = _history_to_messages(history) + [{"role": "user", "content": learner_message}]
    try:
        # Any failure here (missing credential, network, rate limit, bad output)
        # must not break the app — we intentionally fall back to the scripted tutor.
        response = client.with_options(timeout=timeout).messages.create(
            model=model,
            max_tokens=1500,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": TUTOR_SCHEMA}},
            system=_system_prompt(lesson, session_state),
            messages=messages,
        )
        text = next(block.text for block in response.content if block.type == "text")
        payload = json.loads(text)
    except Exception as error:  # noqa: BLE001 - deliberate catch-all -> scripted fallback
        return scripted_turn(session_state, learner_message, lesson, reason=f"api_error:{type(error).__name__}")

    reply = str(payload.get("reply", "")).strip() or _SCRIPTED_BY_PHASE.get(
        session_state.get("phase", "diagnose"), "Tell me more about your thinking."
    )
    return {
        "reply": reply,
        "proposed_observation": _build_proposal(payload.get("proposed_observation"), model),
        "source": "model",
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "fallback_reason": None,
    }
