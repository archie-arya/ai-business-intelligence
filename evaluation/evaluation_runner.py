import json
import statistics
import time
from pathlib import Path

from bi_agent.evaluation import run_agent


ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "questions.json"
RESULTS_DIR = ROOT / "results"
RESULTS_FILE = RESULTS_DIR / "results.json"
REPORT_FILE = RESULTS_DIR / "report.md"


def norm(value):
    return str(value).lower().strip()


def load_questions():
    return json.loads(
        QUESTIONS_FILE.read_text(encoding="utf-8")
    )


def load_existing_results():
    if not RESULTS_FILE.exists():
        return {}

    try:
        results = json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError:
        return {}

    return {
        result["id"]: result
        for result in results
        if "id" in result
    }


def evaluate(question, trace):
    expected_tools = set(
        question.get("expected_tools", [])
    )

    actual_tools = [
        tool["name"]
        for tool in trace.get("tools_called", [])
    ]

    actual_tool_set = set(actual_tools)

    # Exact tool-selection match
    tool_selection_exact = (
        actual_tool_set == expected_tools
    )

    # Tools that were called but were not expected
    unnecessary_tool_calls = len(
        actual_tool_set - expected_tools
    )

    expected_sources = set(
        question.get("expected_sources", [])
    )

    actual_sources = set(
        trace.get("sources_retrieved", [])
    )

    correct_sources = (
        expected_sources & actual_sources
    )

    # Source recall
    if expected_sources:
        source_recall = (
            len(correct_sources)
            / len(expected_sources)
        )
    else:
        source_recall = 1.0

    # Source precision
    if actual_sources:
        source_precision = (
            len(correct_sources)
            / len(actual_sources)
        )
    else:
        source_precision = (
            1.0
            if not expected_sources
            else 0.0
        )

    # Multi-source success
    is_multi_source_question = (
        len(expected_tools) > 1
    )

    if is_multi_source_question:
        multi_source_success = (
            expected_tools.issubset(
                actual_tool_set
            )
        )
    else:
        multi_source_success = None

    # Lightweight deterministic answer check
    answer = norm(
        trace.get("answer", "")
    )

    required_terms = question.get(
        "answer_contains",
        []
    )

    answer_match = all(
        norm(term) in answer
        for term in required_terms
    )

    return {
        "id": question["id"],
        "question": question["question"],
        "expected_tools": question.get(
            "expected_tools",
            [],
        ),
        "actual_tools": actual_tools,
        "tool_selection_exact": tool_selection_exact,
        "unnecessary_tool_calls": unnecessary_tool_calls,
        "expected_sources": question.get(
            "expected_sources",
            [],
        ),
        "actual_sources": trace.get(
            "sources_retrieved",
            [],
        ),
        "source_recall": round(
            source_recall,
            3,
        ),
        "source_precision": round(
            source_precision,
            3,
        ),
        "multi_source_success": multi_source_success,
        "answer_match": answer_match,
        "answer": trace.get(
            "answer",
            "",
        ),
        "latency_ms": trace.get(
            "latency_ms",
            None,
        ),
        "tools_called_detail": trace.get(
            "tools_called",
            [],
        ),
    }


def save_results(results):
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ordered = list(results.values())

    RESULTS_FILE.write_text(
        json.dumps(
            ordered,
            indent=2,
        ),
        encoding="utf-8",
    )


def generate_report(results):
    successful = [
        result
        for result in results.values()
        if "error" not in result
    ]

    failed = [
        result
        for result in results.values()
        if "error" in result
    ]

    if not successful:
        report = """# BI Agent Evaluation Report

No questions have completed successfully yet.
"""

        REPORT_FILE.write_text(
            report,
            encoding="utf-8",
        )

        return

    def average(values):
        if not values:
            return 0

        return sum(values) / len(values)

    # ---------------------------------------------------------
    # Tool-selection accuracy
    # ---------------------------------------------------------

    tool_accuracy = average(
        [
            float(
                result["tool_selection_exact"]
            )
            for result in successful
        ]
    )

    # ---------------------------------------------------------
    # RAG source recall
    # ---------------------------------------------------------

    source_recall = average(
        [
            result["source_recall"]
            for result in successful
        ]
    )

    # ---------------------------------------------------------
    # RAG source precision
    # ---------------------------------------------------------

    source_precision = average(
        [
            result["source_precision"]
            for result in successful
        ]
    )

    # ---------------------------------------------------------
    # Answer matching
    # ---------------------------------------------------------

    answer_match = average(
        [
            float(result["answer_match"])
            for result in successful
        ]
    )

    # ---------------------------------------------------------
    # Unnecessary tool calls
    # ---------------------------------------------------------

    total_unnecessary = sum(
        result["unnecessary_tool_calls"]
        for result in successful
    )

    total_tool_calls = sum(
        len(result["actual_tools"])
        for result in successful
    )

    if total_tool_calls:
        unnecessary_rate = (
            total_unnecessary
            / total_tool_calls
        )
    else:
        unnecessary_rate = 0

    # ---------------------------------------------------------
    # Multi-source success
    # ---------------------------------------------------------

    multi_source_results = [
        result
        for result in successful
        if result["multi_source_success"]
        is not None
    ]

    if multi_source_results:
        multi_source_success = average(
            [
                float(
                    result[
                        "multi_source_success"
                    ]
                )
                for result in multi_source_results
            ]
        )
    else:
        multi_source_success = 0

    # ---------------------------------------------------------
    # Latency
    # ---------------------------------------------------------

    latencies = [
        result["latency_ms"]
        for result in successful
        if result["latency_ms"] is not None
    ]

    latencies.sort()

    mean_latency = (
        average(latencies)
        if latencies
        else 0
    )

    median_latency = (
        statistics.median(latencies)
        if latencies
        else 0
    )

    if latencies:
        p95_index = min(
            len(latencies) - 1,
            max(
                0,
                int(
                    len(latencies) * 0.95
                ) - 1,
            ),
        )

        p95_latency = latencies[
            p95_index
        ]
    else:
        p95_latency = 0

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    report = f"""# BI Agent Evaluation Report

## Progress

- Completed: {len(successful)}
- Failed: {len(failed)}
- Total benchmark questions: {len(results)}

## Metrics

| Metric | Result |
|---|---:|
| Tool-selection exact match | {tool_accuracy:.1%} |
| Unnecessary tool-call rate | {unnecessary_rate:.1%} |
| RAG source recall | {source_recall:.1%} |
| RAG source precision | {source_precision:.1%} |
| Deterministic answer match | {answer_match:.1%} |
| Multi-source success | {multi_source_success:.1%} |
| Mean latency | {mean_latency / 1000:.2f}s |
| Median latency | {median_latency / 1000:.2f}s |
| P95 latency | {p95_latency / 1000:.2f}s |

## Notes

The answer-match metric is only a deterministic
substring check. It is not an LLM-as-judge evaluation.

The benchmark is intentionally sequential because
the current agent uses local Ollama inference.

## Failed Questions

"""

    if failed:
        for result in failed:
            report += (
                f"- **{result['id']}**: "
                f"{result.get('error', 'unknown error')}\\n"
            )
    else:
        report += "None.\\n"

    # ---------------------------------------------------------
    # Slowest questions
    # ---------------------------------------------------------

    report += """
## Slowest Questions

"""

    slowest = sorted(
        successful,
        key=lambda result: (
            result["latency_ms"]
            if result["latency_ms"] is not None
            else 0
        ),
        reverse=True,
    )[:10]

    for result in slowest:
        latency = result["latency_ms"]

        if latency is None:
            latency_text = "unknown"
        else:
            latency_text = (
                f"{latency / 1000:.2f}s"
            )

        report += (
            f"- **{result['id']}** — "
            f"{latency_text} — "
            f"{result['question']}\\n"
        )

    REPORT_FILE.write_text(
        report,
        encoding="utf-8",
    )


def main():
    questions = load_questions()

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing = load_existing_results()

    total = len(questions)

    print()
    print("=" * 80)
    print("BI AGENT EVALUATION")
    print("=" * 80)

    print(
        f"Questions: {total}"
    )

    print(
        f"Already completed: "
        f"{len(existing)}"
    )

    print(
        f"Remaining: "
        f"{total - len(existing)}"
    )

    print("=" * 80)
    print()

    try:

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question_id = question["id"]

            # -------------------------------------------------
            # Resume support
            # -------------------------------------------------

            if question_id in existing:
                print(
                    f"[{index}/{total}] "
                    f"{question_id}: "
                    f"SKIP (already completed)"
                )

                continue

            print(
                f"[{index}/{total}] "
                f"{question_id}: "
                f"{question['question']}"
            )

            started = time.perf_counter()

            try:

                # -------------------------------------------------
                # Run the actual agent
                # -------------------------------------------------

                trace = run_agent(
                    question["question"]
                )

                elapsed_ms = (
                    time.perf_counter()
                    - started
                ) * 1000

                # If run_agent does not provide latency,
                # use the evaluation harness timing.
                if not trace.get(
                    "latency_ms"
                ):
                    trace["latency_ms"] = (
                        elapsed_ms
                    )

                # -------------------------------------------------
                # Evaluate
                # -------------------------------------------------

                result = evaluate(
                    question,
                    trace,
                )

                existing[
                    question_id
                ] = result

                # -------------------------------------------------
                # SAVE IMMEDIATELY
                # -------------------------------------------------

                save_results(
                    existing
                )

                generate_report(
                    existing
                )

                print(
                    "    ✓ completed"
                )

                print(
                    "    latency: "
                    f"{result['latency_ms'] / 1000:.2f}s"
                )

                actual_tools = (
                    result["actual_tools"]
                )

                if actual_tools:
                    tools_text = ", ".join(
                        actual_tools
                    )
                else:
                    tools_text = "none"

                print(
                    "    tools: "
                    + tools_text
                )

                actual_sources = (
                    result[
                        "actual_sources"
                    ]
                )

                if actual_sources:
                    sources_text = ", ".join(
                        actual_sources
                    )
                else:
                    sources_text = "none"

                print(
                    "    sources: "
                    + sources_text
                )

                print()

            except Exception as exc:

                elapsed_ms = (
                    time.perf_counter()
                    - started
                ) * 1000

                # -------------------------------------------------
                # Save failed question too
                # -------------------------------------------------

                existing[
                    question_id
                ] = {
                    "id": question_id,
                    "question": question[
                        "question"
                    ],
                    "error": repr(exc),
                    "latency_ms": elapsed_ms,
                }

                save_results(
                    existing
                )

                generate_report(
                    existing
                )

                print(
                    "    ✗ ERROR "
                    f"({elapsed_ms / 1000:.2f}s)"
                )

                print(
                    f"    {exc}"
                )

                print()

    except KeyboardInterrupt:

        print()
        print("=" * 80)
        print("BENCHMARK INTERRUPTED")
        print("=" * 80)

        print(
            f"Saved "
            f"{len(existing)}/{total} "
            f"questions."
        )

        print()

        print(
            "Run the same command again "
            "to resume."
        )

        print("=" * 80)

        # Make absolutely sure the latest
        # checkpoint/report exists.
        save_results(
            existing
        )

        generate_report(
            existing
        )

        return

    # ---------------------------------------------------------
    # Finished
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)

    print(
        f"Results: "
        f"{RESULTS_FILE}"
    )

    print(
        f"Report:  "
        f"{REPORT_FILE}"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()