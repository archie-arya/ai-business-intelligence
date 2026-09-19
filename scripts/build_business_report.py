"""Create a small, reproducible descriptive BI report from PostgreSQL.

The script keeps SQL in `sql/` and uses psql's CSV mode only to transfer query
results into pandas for visualisation. That separation makes it clear which
layer owns metric definitions (SQL) and which layer owns presentation (Python).
"""

from __future__ import annotations

import os
import subprocess
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
REPORT_DIR = ROOT / "reports"
DATABASE = os.getenv("POSTGRES_DB", "retail_bi")


def run_query(filename: str) -> pd.DataFrame:
    result = subprocess.run(
        [
            "psql", "--dbname", DATABASE, "--csv",
            "--file", str(SQL_DIR / filename),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return pd.read_csv(StringIO(result.stdout))


def save_monthly_chart(monthly: pd.DataFrame) -> None:
    chart_data = monthly.copy()
    chart_data["month_start"] = pd.to_datetime(chart_data["month_start"])
    full_months = chart_data.iloc[:-1]  # Source ends partway through December.

    fig, axis = plt.subplots(figsize=(10, 5))
    axis.plot(full_months["month_start"], full_months["revenue"], marker="o", color="#2563eb")
    axis.set_title("Monthly gross revenue (complete months only)")
    axis.set_xlabel("Month")
    axis.set_ylabel("Revenue (currency units)")
    axis.grid(axis="y", alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "monthly_revenue.png", dpi=160)
    plt.close(fig)


def save_country_chart(countries: pd.DataFrame) -> None:
    top = countries.head(10).iloc[::-1]
    fig, axis = plt.subplots(figsize=(10, 6))
    axis.barh(top["country"], top["revenue"], color="#0f766e")
    axis.set_title("Top 10 countries by gross revenue")
    axis.set_xlabel("Revenue (currency units)")
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "top_countries.png", dpi=160)
    plt.close(fig)


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    monthly = run_query("004_monthly_kpis.sql")
    countries = run_query("005_country_revenue.sql")
    products = run_query("006_product_revenue.sql")
    coverage = run_query("007_data_coverage.sql").iloc[0]

    monthly["month_start"] = pd.to_datetime(monthly["month_start"])
    complete_months = monthly.iloc[:-1].copy()
    latest_complete = complete_months.iloc[-1]
    previous_complete = complete_months.iloc[-2]
    revenue_change = 100 * (latest_complete["revenue"] / previous_complete["revenue"] - 1)

    save_monthly_chart(monthly)
    save_country_chart(countries)

    first_transaction = pd.to_datetime(coverage["first_transaction_at"])
    last_transaction = pd.to_datetime(coverage["last_transaction_at"])
    summary = f"""# Business summary\n\n## Data coverage\n\nThe dataset covers {first_transaction:%d %b %Y} through {last_transaction:%d %b %Y}. December 2011 is incomplete and is excluded from month-over-month commentary.\n\n## Latest complete month\n\nNovember 2011 revenue was {latest_complete['revenue']:,.2f} currency units, across {int(latest_complete['orders']):,} orders. This was {revenue_change:+.1f}% compared with October. Average order value was {latest_complete['average_order_value']:,.2f} currency units.\n\n## Revenue concentration\n\n- Leading country: {countries.iloc[0]['country']} ({countries.iloc[0]['revenue']:,.2f} currency units; {countries.iloc[0]['revenue_share_pct']:.2f}% of gross revenue).\n- Leading product: {products.iloc[0]['product_name']} ({products.iloc[0]['stock_code']}; {products.iloc[0]['revenue']:,.2f} currency units).\n\n## Interpretation guardrails\n\n- The source does not supply a currency code, so monetary values are labeled as currency units.\n- These are **gross sales**: cancellations and returns are currently excluded rather than netted against sales.\n- Revenue does not prove profitability because this dataset has no product cost, shipping cost, or margin data.\n- A country or product ranking shows contribution, not causality. To answer “why did revenue change?”, we will later decompose the change into customers, order frequency, price, and mix.\n"""
    (REPORT_DIR / "business_summary.md").write_text(summary)
    print(summary)
    print(f"Charts saved to {REPORT_DIR}")


if __name__ == "__main__":
    main()
