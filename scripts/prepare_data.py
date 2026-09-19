"""Prepare the raw UCI Online Retail workbook for the first warehouse load.

This script is intentionally boring and deterministic. A later dbt-style
pipeline can replace it, but the data contract should remain visible.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "Online Retail.xlsx"
OUT_DIR = ROOT / "data" / "curated"


def prepare() -> dict[str, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_excel(RAW_PATH)
    raw.columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]

    # Keep the raw row count for an audit report before applying rules.
    raw_rows = len(raw)
    exact_duplicates = int(raw.duplicated().sum())

    df = raw.drop_duplicates().copy()
    df["invoice_no"] = df["invoice_no"].astype(str).str.strip()
    df["stock_code"] = df["stock_code"].astype(str).str.strip()
    df["description"] = df["description"].astype("string").str.strip()
    df["country"] = df["country"].astype("string").str.strip()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="raise")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["is_cancelled"] = df["invoice_no"].str.upper().str.startswith("C")
    df["line_revenue"] = (df["quantity"] * df["unit_price"]).round(2)

    # Sales fact: cancellations and non-positive sales lines are not revenue.
    sales = df.loc[
        (~df["is_cancelled"])
        & (df["quantity"] > 0)
        & (df["unit_price"] >= 0)
    ].copy()
    sales["order_date"] = sales["invoice_date"].dt.date
    sales["year"] = sales["invoice_date"].dt.year
    sales["quarter"] = sales["invoice_date"].dt.quarter
    sales["month"] = sales["invoice_date"].dt.to_period("M").astype(str)

    # Product description is not perfectly stable in the source. Select the
    # most frequent non-null label per stock code and retain an unknown label
    # when the source has no description at all.
    product_labels = (
        sales.dropna(subset=["description"])
        .groupby(["stock_code", "description"], as_index=False)
        .size()
        .sort_values(["stock_code", "size", "description"], ascending=[True, False, True])
        .drop_duplicates("stock_code")
        .rename(columns={"description": "product_name"})[["stock_code", "product_name"]]
    )
    products = sales[["stock_code"]].drop_duplicates().merge(product_labels, on="stock_code", how="left")
    products["product_name"] = products["product_name"].fillna("Unknown product")

    customers = (
        sales.dropna(subset=["customer_id"])
        .groupby(["customer_id", "country"], as_index=False)
        .size()
        .sort_values(["customer_id", "size", "country"], ascending=[True, False, True])
        .drop_duplicates("customer_id")[["customer_id", "country"]]
    )

    calendar = pd.DataFrame({"calendar_date": pd.date_range(sales["order_date"].min(), sales["order_date"].max(), freq="D")})
    calendar["year"] = calendar["calendar_date"].dt.year
    calendar["quarter"] = calendar["calendar_date"].dt.quarter
    calendar["month"] = calendar["calendar_date"].dt.to_period("M").astype(str)
    calendar["month_name"] = calendar["calendar_date"].dt.strftime("%B")

    sales_columns = [
        "invoice_no", "stock_code", "description", "quantity", "invoice_date",
        "unit_price", "customer_id", "country", "line_revenue", "order_date",
        "year", "quarter", "month",
    ]
    sales[sales_columns].to_csv(OUT_DIR / "fact_sales_line.csv", index=False)
    products.to_csv(OUT_DIR / "dim_product.csv", index=False)
    customers.to_csv(OUT_DIR / "dim_customer.csv", index=False)
    calendar.to_csv(OUT_DIR / "dim_calendar.csv", index=False)

    audit = pd.DataFrame(
        [
            {"metric": "raw_rows", "value": raw_rows},
            {"metric": "exact_duplicate_rows_removed", "value": exact_duplicates},
            {"metric": "source_cancellation_rows", "value": int(df["is_cancelled"].sum())},
            {"metric": "sales_fact_rows", "value": len(sales)},
            {"metric": "product_count", "value": len(products)},
            {"metric": "customer_count_with_id", "value": len(customers)},
            {"metric": "calendar_days", "value": len(calendar)},
            {"metric": "sales_revenue", "value": round(float(sales["line_revenue"].sum()), 2)},
        ]
    )
    audit.to_csv(OUT_DIR / "audit_metrics.csv", index=False)
    return dict(zip(audit["metric"], audit["value"]))


if __name__ == "__main__":
    metrics = prepare()
    for name, value in metrics.items():
        print(f"{name}: {value}")
