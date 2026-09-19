SELECT
    MIN(invoice_date) AS first_transaction_at,
    MAX(invoice_date) AS last_transaction_at
FROM retail.fact_sales_line;
