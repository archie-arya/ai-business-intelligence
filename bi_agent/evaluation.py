import time
from typing import Any

from bi_agent.agent import graph


def extract_rag_sources(tool_results: list[dict]) -> list[str]:
    """
    Extract document names returned by the RAG tool.
    """

    sources = []

    for result in tool_results:

        if result["name"] != "search_business_documents":
            continue

        content = result["content"]

        for line in content.splitlines():

            if line.startswith("Source:"):
                source = line.replace("Source:", "").strip()

                if source not in sources:
                    sources.append(source)

    return sources


def run_agent(question: str) -> dict[str, Any]:
    """
    Run the LangGraph agent once and capture its execution trace.
    """

    start = time.perf_counter()

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    messages = result.get("messages", [])

    tool_calls = []
    tool_results = []

    for message in messages:

        # AI messages can contain tool calls.
        if hasattr(message, "tool_calls") and message.tool_calls:

            for call in message.tool_calls:

                tool_calls.append(
                    {
                        "name": call["name"],
                        "args": call.get("args", {}),
                    }
                )

        # ToolMessage contains the actual tool output.
        if getattr(message, "type", None) == "tool":

            tool_results.append(
                {
                    "name": getattr(
                        message,
                        "name",
                        None,
                    ),
                    "content": message.content,
                }
            )

    # Find the final AI response.
    final_answer = ""

    for message in reversed(messages):

        if getattr(message, "type", None) == "ai":

            if message.content:
                final_answer = message.content
                break

    sources_retrieved = extract_rag_sources(
        tool_results
    )

    return {
        "question": question,
        "tools_called": tool_calls,
        "tool_results": tool_results,
        "sources_retrieved": sources_retrieved,
        "answer": final_answer,
        "latency_ms": round(latency_ms, 2),
    }