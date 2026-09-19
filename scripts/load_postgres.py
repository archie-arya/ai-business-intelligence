"""Create the retail warehouse schema and load the curated CSV files.

Requires a running local PostgreSQL service and the `psql` command on PATH.
Run from the repository root:
    .venv/bin/python scripts/load_postgres.py
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "curated"
DATABASE = os.getenv("POSTGRES_DB", "retail_bi")


def psql(*args: str) -> None:
    subprocess.run(
        ["psql", "--set", "ON_ERROR_STOP=1", "--dbname", DATABASE, *args],
        check=True,
    )


def copy_csv(table: str, columns: list[str], filename: str) -> None:
    path = (DATA_DIR / filename).as_posix().replace("'", "''")
    column_list = ", ".join(columns)
    command = f"\\copy {table} ({column_list}) FROM '{path}' WITH (FORMAT csv, HEADER true)"
    psql("--command", command)


def main() -> None:
    required_files = [
        "dim_product.csv",
        "dim_customer.csv",
        "dim_calendar.csv",
        "fact_sales_line.csv",
    ]
    missing = [name for name in required_files if not (DATA_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing curated files: {', '.join(missing)}. Run prepare_data.py first.")

    psql("--file", str(ROOT / "sql" / "001_create_schema.sql"))
    copy_csv("retail.dim_product", ["stock_code", "product_name"], "dim_product.csv")
    copy_csv("retail.dim_customer", ["customer_id", "country"], "dim_customer.csv")
    copy_csv(
        "retail.dim_calendar",
        ["calendar_date", "year", "quarter", "month", "month_name"],
        "dim_calendar.csv",
    )
    copy_csv(
        "retail.fact_sales_line",
        [
            "invoice_no", "stock_code", "description", "quantity", "invoice_date",
            "unit_price", "customer_id", "country", "line_revenue", "order_date",
            "year", "quarter", "month",
        ],
        "fact_sales_line.csv",
    )
    psql("--command", "ANALYZE retail.fact_sales_line")
    psql("--file", str(ROOT / "sql" / "003_quality_checks.sql"))


if __name__ == "__main__":
    main()
