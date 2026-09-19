"""Guarded, read-only access to the project PostgreSQL database."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import psycopg


MAX_ROWS = 200
FORBIDDEN_KEYWORDS = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|"
    r"COPY|CALL|DO|VACUUM|ANALYZE|SET|RESET|SHOW|PREPARE|EXECUTE|DEALLOCATE)\b",
    re.IGNORECASE,
)
LEADING_COMMENTS = re.compile(r"^(?:\s|--[^\n]*(?:\n|$)|/\*.*?\*/)*", re.DOTALL)


class UnsafeQueryError(ValueError):
    """Raised before a query reaches PostgreSQL."""


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    truncated: bool


def validate_read_only_query(query: str) -> str:
    """Allow exactly one SELECT/WITH statement and reject obvious write commands."""
    normalized = query.strip()
    if normalized.endswith(";"):
        normalized = normalized[:-1].strip()
    if not normalized or ";" in normalized:
        raise UnsafeQueryError("Only one SQL statement is allowed.")

    statement = LEADING_COMMENTS.sub("", normalized)
    if not re.match(r"^(SELECT|WITH)\b", statement, re.IGNORECASE):
        raise UnsafeQueryError("Only SELECT queries (including WITH ... SELECT) are allowed.")
    if FORBIDDEN_KEYWORDS.search(statement):
        raise UnsafeQueryError("The query includes a command outside the read-only allowlist.")
    return normalized


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value.isoformat() if hasattr(value, "isoformat") else value


def execute_read_only_query(query: str, database: str | None = None) -> QueryResult:
    """Execute a bounded query in a read-only, time-limited transaction."""
    safe_query = validate_read_only_query(query)
    dbname = database or os.getenv("POSTGRES_DB", "retail_bi")

    try:
        with psycopg.connect(dbname=dbname) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SET LOCAL statement_timeout = '5s'")
                cursor.execute(safe_query)
                columns = [column.name for column in cursor.description]
                raw_rows = cursor.fetchmany(MAX_ROWS + 1)
    except psycopg.Error as error:
        raise ValueError(f"PostgreSQL rejected the generated read-only query: {error}") from error

    return QueryResult(
        columns=columns,
        rows=[dict(zip(columns, map(_json_value, row), strict=True)) for row in raw_rows[:MAX_ROWS]],
        truncated=len(raw_rows) > MAX_ROWS,
    )
