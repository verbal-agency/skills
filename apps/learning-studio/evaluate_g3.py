#!/usr/bin/env python3
"""Print the deterministic G3 fixture report."""

from __future__ import annotations

import json
from pathlib import Path

from grading import evaluate_labeled_cases


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "packages" / "pytorch-foundations" / "evidence" / "g3_labeled_cases.jsonl"


def main() -> None:
    cases = [json.loads(line) for line in FIXTURES.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(evaluate_labeled_cases(cases), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
