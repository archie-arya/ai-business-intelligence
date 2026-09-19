"""Run fast invariants and print baseline metrics for the curated dataset."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "curated"


def main() -> None:
    fact = pd.read_csv(DATA / "fact_sales_line.csv", dtype={"invoice_no": "string", "stock_code": "string"})
    products = pd.read_csv(DATA / "dim_product.csv", dtype={"stock_code": "string"})
    customers = pd.read_csv(DATA / "dim_customer.csv")
    calendar = pd.read_csv(DATA / "dim_calendar.csv", parse_dates=["calendar_date"])
    fact["order_date"] = pd.to_datetime(fact["order_date"])

    assert (fact["quantity"] > 0).all()
    assert (fact["unit_price"] >= 0).all()
    assert fact["stock_code"].isin(products["stock_code"]).all()
    assert fact["customer_id"].dropna().isin(customers["customer_id"]).all()
    assert fact["order_date"].isin(calendar["calendar_date"]).all()

    print("validation: PASS")
    quarterly = (
        fact.groupby(["year", "quarter"], as_index=False)["line_revenue"]
        .sum()
        .assign(line_revenue=lambda frame: frame["line_revenue"].round(2))
    )
    print("\nRevenue by quarter:")
    print(quarterly.to_string(index=False))

    top_products = (
        fact.groupby(["stock_code", "description"], dropna=False, as_index=False)["line_revenue"]
        .sum()
        .sort_values("line_revenue", ascending=False)
        .head(5)
    )
    print("\nTop 5 products:")
    print(top_products.to_string(index=False))
    print(f"\nDistinct invoices: {fact['invoice_no'].nunique()}")


if __name__ == "__main__":
    main()
