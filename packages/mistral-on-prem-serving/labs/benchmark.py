#!/usr/bin/env python3
"""Small repeatable OpenAI-compatible serving benchmark.

It measures full-response latency and completion-token throughput. Run it only
against an endpoint you own, with a workload representative of the learner's
target; it is not a model-quality or safety benchmark.
"""

import argparse
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return None
    index = min(len(ordered) - 1, round((len(ordered) - 1) * fraction))
    return ordered[index]


def run_one(base_url, api_key, model, prompt):
    client = OpenAI(base_url=base_url, api_key=api_key)
    started = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.perf_counter() - started
    usage = response.usage
    tokens = getattr(usage, "completion_tokens", 0) if usage else 0
    return elapsed, tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8080/v1"))
    parser.add_argument("--api-key", default=os.getenv("API_KEY", "local"))
    parser.add_argument("--model", default=os.getenv("MODEL_ID", "local-model"))
    parser.add_argument("--prompt", default="Say hello in one short sentence.")
    parser.add_argument("--requests", type=int, default=8)
    parser.add_argument("--concurrency", type=int, nargs="+", default=[1, 4])
    args = parser.parse_args()

    if args.requests < 1 or any(level < 1 for level in args.concurrency):
        parser.error("requests and concurrency must be positive")

    # Warm-up separates model loading from the measured workload.
    run_one(args.base_url, args.api_key, args.model, args.prompt)
    for level in args.concurrency:
        started = time.perf_counter()
        results = []
        failures = []
        with ThreadPoolExecutor(max_workers=level) as pool:
            futures = [
                pool.submit(run_one, args.base_url, args.api_key, args.model, args.prompt)
                for _ in range(args.requests)
            ]
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as error:  # record failures as evidence
                    failures.append(type(error).__name__ + ": " + str(error))
        wall_time = time.perf_counter() - started
        latencies = [elapsed for elapsed, _ in results]
        tokens = sum(count for _, count in results)
        print(json.dumps({
            "model": args.model,
            "base_url": args.base_url,
            "requests": args.requests,
            "concurrency": level,
            "successful_requests": len(results),
            "failures": failures,
            "latency_seconds": {
                "p50": percentile(latencies, 0.50),
                "p95": percentile(latencies, 0.95),
                "mean": statistics.mean(latencies) if latencies else None,
            },
            "completion_tokens": tokens,
            "completion_tokens_per_second": tokens / wall_time if wall_time else None,
        }, sort_keys=True))


if __name__ == "__main__":
    main()
