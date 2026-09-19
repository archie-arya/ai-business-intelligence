"""The compact schema contract supplied to the model.

The model receives this rather than unrestricted database access or an
unbounded schema dump. Update it alongside SQL migrations.
"""

SCHEMA_CONTEXT = """
PostgreSQL schema: retail

retail.fact_sales_line (one row per invoice/product line; valid non-cancelled gross sale)
- invoice_no TEXT: order identifier; an order can have many sales lines
- stock_code TEXT: joins dim_product.stock_code
- description TEXT: source description, can be inconsistent for the same code
- quantity INTEGER: positive units sold
- invoice_date TIMESTAMP
- unit_price NUMERIC: price per unit
- customer_id INTEGER nullable: joins dim_customer.customer_id
- country TEXT
- line_revenue NUMERIC: quantity * unit_price
- order_date DATE
- year SMALLINT, quarter SMALLINT, month TEXT (YYYY-MM)

retail.dim_product
- stock_code TEXT primary key
- product_name TEXT: canonical product label

retail.dim_customer
- customer_id INTEGER primary key
- country TEXT

Business definitions:
- Revenue means gross sales: SUM(line_revenue). Cancellations/returns are excluded.
- Order count means COUNT(DISTINCT invoice_no), not COUNT(*).
- Average order value is revenue divided by distinct invoice count.
- For country revenue, group by fact_sales_line.country. Do not join through
  dim_customer, because customer_id is nullable and that would omit valid sales.
- The dataset covers 2010-12-01 to 2011-12-09. December 2011 is incomplete.
- The source does not provide a currency code. Describe monetary values as
  "currency units" rather than assuming a currency symbol.
""".strip()
