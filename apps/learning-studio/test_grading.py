#!/usr/bin/env python3
"""Contract tests for the G3 deterministic evidence graders."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from grading import evaluate_labeled_cases, grade_choice, grade_open_response


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "packages" / "pytorch-foundations" / "evidence" / "g3_labeled_cases.jsonl"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in FIXTURES.read_text(encoding="utf-8").splitlines() if line.strip()]


class GradingTests(unittest.TestCase):
    def test_open_response_contains_structured_observation_and_provenance(self) -> None:
        observation = grade_open_response(
            "diagnostic.gradient-accumulation.baseline",
            "backward accumulates into the previous .grad, so zero_grad clears it before the next batch.",
        )
        self.assertEqual(observation["schema"], "learning-evidence/v1")
        self.assertEqual(observation["label"], "gradient_accumulation")
        self.assertEqual(observation["status"], "supported")
        self.assertEqual(observation["result"], "pass")
        self.assertTrue(observation["evidence_spans"])
        self.assertTrue(observation["alternatives"])
        self.assertEqual(observation["evaluator"]["type"], "deterministic")
        self.assertEqual(observation["evaluator"]["rubric_version"], "pt-g3-v1")
        self.assertNotIn("score", observation)

    def test_open_response_can_abstain_on_sparse_evidence(self) -> None:
        observation = grade_open_response(
            "diagnostic.gradient-accumulation.baseline",
            "I am unsure; it has something to do with training.",
        )
        self.assertEqual(observation["status"], "abstained")
        self.assertEqual(observation["result"], "abstain")
        self.assertEqual(observation["failure_type"], "knowledge_gap")

    def test_choice_grader_is_categorical_and_distinguishes_slip(self) -> None:
        passed = grade_choice("practice.gradient-accumulation.repair", 0, 0)
        wrong = grade_choice("practice.gradient-accumulation.repair", 1, 0)
        slip = grade_choice("practice.gradient-accumulation.repair", None, 0)
        self.assertEqual(passed["result"], "pass")
        self.assertEqual(wrong["failure_type"], "procedural_error")
        self.assertEqual(slip["failure_type"], "execution_slip")
        self.assertNotIn("score", passed)

    def test_seeded_cases_cover_failure_types_and_report_metrics(self) -> None:
        cases = load_cases()
        report = evaluate_labeled_cases(cases)
        self.assertEqual(report["cases"], 10)
        self.assertGreaterEqual(report["precision_macro"], 0.99)
        self.assertGreaterEqual(report["recall_macro"], 0.99)
        self.assertGreater(report["abstention_rate"], 0.0)
        self.assertEqual(report["calibration"]["status"], "not_applicable")
        self.assertEqual(
            set(report["failure_types"]),
            {"execution_slip", "knowledge_gap", "misconception", "procedural_error", "transfer_failure"},
        )


if __name__ == "__main__":
    unittest.main()
