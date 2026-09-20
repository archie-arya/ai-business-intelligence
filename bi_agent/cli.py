"""Command-line entry point for the LangGraph BI agent."""

from __future__ import annotations

import argparse

from bi_agent.agent import ask


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask the local BI agent a database question."
    )
    parser.add_argument("question")
    args = parser.parse_args()

    result = ask(args.question)

    final_message = result["messages"][-1]

    print(final_message.content)


if __name__ == "__main__":
    main()