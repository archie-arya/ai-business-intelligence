-- Monthly business health metrics at the invoice (order) grain.
WITH invoices AS (
    SELECT
        invoice_no,
        DATE_TRUNC('month', order_date)::DATE AS month_start,
        MAX(customer_id) AS customer_id,
        SUM(line_revenue) AS order_value
    FROM retail.fact_sales_line
    GROUP BY invoice_no, DATE_TRUNC('month', order_date)::DATE
)
SELECT
    month_start,
    ROUND(SUM(order_value), 2) AS revenue,
    COUNT(*) AS orders,
    ROUND(SUM(order_value) / COUNT(*), 2) AS average_order_value,
    COUNT(DISTINCT customer_id) AS active_customers
FROM invoices
GROUP BY month_start
ORDER BY month_start;
