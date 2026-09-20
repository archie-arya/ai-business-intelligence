"""LangGraph-based autonomous BI agent."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from bi_agent.model import get_model
from bi_agent.schema import SCHEMA_CONTEXT
from bi_agent.sql_tool import query_database


SYSTEM_PROMPT = f"""You are a business intelligence agent for a retail analytics database.

Your job is to answer the user's business questions using the available tools.

{SCHEMA_CONTEXT}

Agent rules:
- Use the database tool whenever the answer requires data from the retail database.
- Do not invent values.
- Revenue means gross sales: SUM(line_revenue).
- Orders mean COUNT(DISTINCT invoice_no).
- Average order value means revenue divided by distinct invoice count.
- For country revenue, use fact_sales_line.country.
- For quarterly analysis, always keep year and quarter together.
- December 2011 is incomplete.
- The source dataset does not provide a currency code, so call monetary values
  "currency units".
- Prefer canonical product_name from retail.dim_product when displaying products.
- If a tool returns an error, inspect the error and decide whether another
  tool call can resolve it.
- Stop when you have enough information to answer the user's question.
"""


def build_graph():
    model = get_model()

    tools = [query_database]
    model_with_tools = model.bind_tools(tools)

    def agent_node(state: MessagesState):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        response = model_with_tools.invoke(messages)

        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge("tools", "agent")

    return builder.compile()


graph = build_graph()


def ask(question: str):
    """Run the BI agent for one user question."""
    return graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )