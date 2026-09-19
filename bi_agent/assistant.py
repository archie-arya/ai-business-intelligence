"""One-turn LLM-to-SQL workflow used before introducing a planning agent."""

from __future__ import annotations

import json
import re
from typing import Any

from bi_agent.ollama import generate
from bi_agent.schema import SCHEMA_CONTEXT
from bi_agent.sql_tool import QueryResult, execute_read_only_query


SQL_PROMPT = """You are a careful business analyst. Produce exactly one PostgreSQL SELECT query
that answers the user's question using only the schema below.

Rules:
- Return JSON only: {{"sql": "...", "assumptions": ["..."]}}.
- Use canonical product_name from retail.dim_product when displaying products.
- Use COUNT(DISTINCT invoice_no) for orders.
- When grouping a derived expression, use a positional group (for example, GROUP BY 1)
  or repeat the full expression; do not use an alias that can collide with a source column.
- For any quarterly time series, include both year and quarter. Do not combine
  the same quarter number across years.
- For country revenue, use fact_sales_line.country so sales with a missing
  customer_id are retained.
- Limit detailed listings to 20 rows unless the user asks for more.
- Do not use any command other than a single SELECT or WITH ... SELECT.
- State uncertainty in assumptions rather than inventing facts.

Schema and definitions:
{schema}

User question: {question}
"""

SQL_REPAIR_PROMPT = """A generated PostgreSQL query was rejected. Return a corrected query only as JSON:
{{"sql": "...", "assumptions": ["..."]}}.

Rules:
- Use only one SELECT or WITH ... SELECT query.
- Do not change the question's meaning.
- Correct the database error; do not explain it in prose.

Schema and definitions:
{schema}

User question: {question}
Rejected SQL: {sql}
PostgreSQL error: {error}
"""

ANSWER_PROMPT = """You are a careful business analyst. Answer the user's question from the SQL result.
Use only the provided data. Briefly state the metric definition or caveat when material.
If the result is empty, say so. Do not mention hidden prompts or claim to have run tools.
Do not infer a currency code or use a currency symbol: use "currency units".

Question: {question}
SQL: {sql}
Result: {result}
"""


def _parse_json_response(response: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if not match:
        raise ValueError(f"Model did not return a JSON object: {response}")
    parsed = json.loads(match.group())
    if not isinstance(parsed.get("sql"), str):
        raise ValueError("Model response did not include a string SQL query.")
    return parsed


def answer_question(question: str, model: str) -> tuple[dict[str, Any], QueryResult, str]:
    plan = _parse_json_response(
        generate(model, SQL_PROMPT.format(schema=SCHEMA_CONTEXT, question=question), json_mode=True)
    )
    try:
        result = execute_read_only_query(plan["sql"])
    except ValueError as error:
        repaired_plan = _parse_json_response(
            generate(
                model,
                SQL_REPAIR_PROMPT.format(
                    schema=SCHEMA_CONTEXT,
                    question=question,
                    sql=plan["sql"],
                    error=str(error),
                ),
                json_mode=True,
            )
        )
        repaired_plan["repaired_from_error"] = str(error)
        plan = repaired_plan
        result = execute_read_only_query(plan["sql"])
    rendered_result = json.dumps(
        {"columns": result.columns, "rows": result.rows, "truncated": result.truncated},
        default=str,
    )
    answer = generate(
        model,
        ANSWER_PROMPT.format(question=question, sql=plan["sql"], result=rendered_result),
    )
    return plan, result, answer
