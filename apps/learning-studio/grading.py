"""Versioned, deterministic graders for the first PyTorch evidence slice.

The grader returns categorical observations, not model confidence.  Its output
is deliberately boring: matched evidence spans, explicit alternatives, an
abstention path, and evaluator provenance that can be replayed from an event.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Iterable


EVIDENCE_SCHEMA = "learning-evidence/v1"
PACKAGE_VERSION = "0.1.0"

OPEN_RESPONSE_RUBRICS = {
    "diagnostic.gradient-accumulation.baseline": {
        "evaluator_id": "rubric-pt-g3-gradient-accumulation",
        "task": "baseline",
    },
    "review.gradient-accumulation.transfer": {
        "evaluator_id": "rubric-pt-g3-gradient-accumulation-transfer",
        "task": "transfer",
    },
}


def _evaluator(evaluator_id: str) -> dict[str, Any]:
    return {
        "type": "deterministic",
        "evaluator_id": evaluator_id,
        "evaluator_version": 1,
        "rubric_version": "pt-g3-v1",
    }


def _find_spans(text: str, patterns: Iterable[str]) -> list[str]:
    spans: list[str] = []
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = match.group(0).strip()
            if value and value not in spans:
                spans.append(value)
    return spans


def _observation(
    *,
    activity_id: str,
    evaluator_id: str,
    label: str,
    status: str,
    result: str,
    spans: list[str],
    alternatives: list[str],
    failure_type: str | None,
    detail: str,
) -> dict[str, Any]:
    kind = "good" if result == "pass" else "warn" if result == "fail" else "neutral"
    return {
        "schema": EVIDENCE_SCHEMA,
        "activity_id": activity_id,
        "label": label,
        "status": status,
        "result": result,
        "failure_type": failure_type,
        "evidence_spans": spans,
        "alternatives": alternatives,
        "evaluator": _evaluator(evaluator_id),
        "evidence_refs": [activity_id],
        # Presentation fields keep the existing evidence panel useful while
        # the structured fields above remain the source of truth.
        "kind": kind,
        "title": f"{label.replace('_', ' ').title()} ({status})",
        "detail": detail,
    }


def _grade_baseline(activity_id: str, response: str, evaluator_id: str) -> dict[str, Any]:
    text = response.strip()
    accumulation = _find_spans(text, [r"accumul\w*", r"carry(?:[- ]?over)?", r"previous", r"left over"])
    reset = _find_spans(text, [r"zero[_ ]grad", r"clear\w*", r"reset\w*"])
    misconception = _find_spans(
        text,
        [
            r"backward (?:replaces|overwrites|resets)",
            r"zero[_ ]grad[^.]{0,60}(?:after|following) backward",
            r"step[^.]{0,40}before backward",
            r"zero[_ ]grad is cosmetic",
        ],
    )
    spans = misconception or accumulation + reset
    if misconception:
        return _observation(
            activity_id=activity_id,
            evaluator_id=evaluator_id,
            label="stale_gradient_accumulation",
            status="supported",
            result="fail",
            spans=spans,
            alternatives=["optimizer_ordering_error", "intentional_microbatch_accumulation"],
            failure_type="misconception",
            detail="The response treats backward as replacing gradients or places the reset after the contribution.",
        )
    if accumulation and reset:
        return _observation(
            activity_id=activity_id,
            evaluator_id=evaluator_id,
            label="gradient_accumulation",
            status="supported",
            result="pass",
            spans=spans,
            alternatives=["intentional_microbatch_accumulation"],
            failure_type=None,
            detail="Names gradient carry-over and the reset that separates ordinary minibatch updates.",
        )
    return _observation(
        activity_id=activity_id,
        evaluator_id=evaluator_id,
        label="gradient_accumulation",
        status="abstained",
        result="abstain",
        spans=spans,
        alternatives=["stale_gradient_accumulation", "optimizer_ordering_error"],
        failure_type="knowledge_gap",
        detail="The response does not contain enough observable mechanism to distinguish a gap from a related ordering error.",
    )


def _grade_transfer(activity_id: str, response: str, evaluator_id: str) -> dict[str, Any]:
    text = response.strip()
    accumulation = _find_spans(text, [r"accumul\w*", r"carry(?:[- ]?over)?", r"previous", r"larger"])
    mechanism = _find_spans(text, [r"\.grad", r"gradient", r"clear\w*", r"zero[_ ]grad", r"reset\w*"])
    if accumulation and mechanism:
        return _observation(
            activity_id=activity_id,
            evaluator_id=evaluator_id,
            label="gradient_accumulation",
            status="supported",
            result="pass",
            spans=accumulation + [span for span in mechanism if span not in accumulation],
            alternatives=["optimizer_ordering_error", "intentional_microbatch_accumulation"],
            failure_type=None,
            detail="Transfers the accumulation mechanism to a new prompt and names the control that prevents accidental carry-over.",
        )
    if mechanism:
        return _observation(
            activity_id=activity_id,
            evaluator_id=evaluator_id,
            label="gradient_accumulation",
            status="candidate",
            result="fail",
            spans=mechanism,
            alternatives=["knowledge_gap", "stale_gradient_accumulation"],
            failure_type="transfer_failure",
            detail="Mentions a related control but does not explain what carries between batches.",
        )
    return _observation(
        activity_id=activity_id,
        evaluator_id=evaluator_id,
        label="gradient_accumulation",
        status="abstained",
        result="abstain",
        spans=[],
        alternatives=["knowledge_gap", "stale_gradient_accumulation"],
        failure_type="knowledge_gap",
        detail="The transfer response contains no evidence that can be evaluated against the target mechanism.",
    )


def grade_open_response(activity_id: str, response: str, package_version: str = PACKAGE_VERSION) -> dict[str, Any]:
    """Grade one authored open-response activity without a model call."""

    if package_version != PACKAGE_VERSION:
        raise ValueError(f"unsupported package version: {package_version}")
    if not isinstance(response, str):
        raise ValueError("response must be text")
    rubric = OPEN_RESPONSE_RUBRICS.get(activity_id)
    if rubric is None:
        raise ValueError(f"unsupported open-response activity: {activity_id}")
    if rubric["task"] == "baseline":
        return _grade_baseline(activity_id, response, rubric["evaluator_id"])
    return _grade_transfer(activity_id, response, rubric["evaluator_id"])


def grade_choice(
    activity_id: str,
    selected_index: Any,
    expected_index: int,
    package_version: str = PACKAGE_VERSION,
) -> dict[str, Any]:
    """Grade a bounded choice activity with an exact categorical result."""

    if package_version != PACKAGE_VERSION:
        raise ValueError(f"unsupported package version: {package_version}")
    evaluator_id = "deterministic-pt-g3-repair"
    try:
        selected = int(selected_index)
    except (TypeError, ValueError):
        selected = None
    if selected is None or selected < 0:
        return _observation(
            activity_id=activity_id,
            evaluator_id=evaluator_id,
            label="execution_slip",
            status="abstained",
            result="abstain",
            spans=["no valid option selected"],
            alternatives=["procedural_error", "knowledge_gap"],
            failure_type="execution_slip",
            detail="The grader received no valid choice, so it abstains instead of inferring a misconception.",
        )
    if selected == expected_index:
        return _observation(
            activity_id=activity_id,
            evaluator_id=evaluator_id,
            label="training_loop_order",
            status="supported",
            result="pass",
            spans=[f"selected option {selected}"],
            alternatives=["intentional_microbatch_accumulation"],
            failure_type=None,
            detail="The selected repair matches the authored training-loop ordering check.",
        )
    return _observation(
        activity_id=activity_id,
        evaluator_id=evaluator_id,
        label="procedural_error",
        status="supported",
        result="fail",
        spans=[f"selected option {selected}", f"expected option {expected_index}"],
        alternatives=["stale_gradient_accumulation", "optimizer_ordering_error"],
        failure_type="procedural_error",
        detail="The selected operation does not satisfy the authored training-loop ordering check.",
    )


def grade_case(case: dict[str, Any], package_version: str = PACKAGE_VERSION) -> dict[str, Any]:
    mode = case.get("mode")
    if mode == "open_response":
        return grade_open_response(case["activity_id"], case.get("response", ""), package_version)
    if mode == "choice":
        return grade_choice(case["activity_id"], case.get("selected_index"), case["expected_index"], package_version)
    raise ValueError(f"unsupported fixture mode: {mode}")


def evaluate_labeled_cases(cases: Iterable[dict[str, Any]], package_version: str = PACKAGE_VERSION) -> dict[str, Any]:
    """Return reproducible classification metrics for the seeded fixture set."""

    rows = []
    for case in cases:
        observation = grade_case(case, package_version)
        predicted = "__abstain__" if observation["status"] == "abstained" else observation["label"]
        expected = case["expected_label"]
        rows.append({"id": case["id"], "expected": expected, "predicted": predicted, "observation": observation})

    labels = sorted({row["expected"] for row in rows} | {row["predicted"] for row in rows})
    by_label: dict[str, dict[str, int]] = {}
    for label in labels:
        tp = sum(row["expected"] == label and row["predicted"] == label for row in rows)
        fp = sum(row["expected"] != label and row["predicted"] == label for row in rows)
        fn = sum(row["expected"] == label and row["predicted"] != label for row in rows)
        by_label[label] = {
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "precision": round(tp / (tp + fp), 4) if tp + fp else 0.0,
            "recall": round(tp / (tp + fn), 4) if tp + fn else 0.0,
        }
    active_labels = [label for label in labels if label != "__abstain__"]
    precision = sum(by_label[label]["precision"] for label in active_labels) / len(active_labels) if active_labels else 0.0
    recall = sum(by_label[label]["recall"] for label in active_labels) / len(active_labels) if active_labels else 0.0
    abstentions = sum(row["predicted"] == "__abstain__" for row in rows)
    failure_types = Counter(
        row["observation"]["failure_type"]
        for row in rows
        if row["observation"].get("failure_type")
    )
    return {
        "schema": "learning-evaluation/v1",
        "package_version": package_version,
        "cases": len(rows),
        "precision_macro": round(precision, 4),
        "recall_macro": round(recall, 4),
        "abstention_rate": round(abstentions / len(rows), 4) if rows else 0.0,
        "abstentions": abstentions,
        "failure_types": dict(sorted(failure_types.items())),
        "per_label": by_label,
        "calibration": {
            "status": "not_applicable",
            "numeric_scores": 0,
            "reason": "The deterministic evaluator emits categorical results and no probability scores.",
        },
        "rows": rows,
    }
