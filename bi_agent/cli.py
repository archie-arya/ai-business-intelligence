"""Command-line entry point for the first SQL-tool prototype."""

from __future__ import annotations

import argparse
import os
import sys

from bi_agent.assistant import answer_question
from bi_agent.sql_tool import UnsafeQueryError


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the local BI assistant a database question.")
    parser.add_argument("question")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3:latest"))
    parser.add_argument("--show-sql", action="store_true")
    args = parser.parse_args()

    try:
        plan, result, answer = answer_question(args.question, args.model)
    except (UnsafeQueryError, ValueError, OSError) as error:
        print(f"Assistant could not complete the query: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    if args.show_sql:
        print("Generated SQL:\n" + plan["sql"])
        if plan.get("repaired_from_error"):
            print("\nSQL was repaired after PostgreSQL rejected the first attempt.")
        if plan.get("assumptions"):
            print("\nModel assumptions:\n- " + "\n- ".join(plan["assumptions"]))
        print(f"\nRows returned: {len(result.rows)}" + (" (truncated)" if result.truncated else ""))
        print()
    print(answer)


if __name__ == "__main__":
    main()
