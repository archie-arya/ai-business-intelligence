-- The load is correct only if these values match the Python validation output.

SELECT 'sales_lines' AS metric, COUNT(*)::TEXT AS value
FROM retail.fact_sales_line
UNION ALL
SELECT 'products', COUNT(*)::TEXT FROM retail.dim_product
UNION ALL
SELECT 'identified_customers', COUNT(*)::TEXT FROM retail.dim_customer
UNION ALL
SELECT 'calendar_days', COUNT(*)::TEXT FROM retail.dim_calendar
UNION ALL
SELECT 'gross_revenue', TO_CHAR(SUM(line_revenue), 'FM999999999999990.00')
FROM retail.fact_sales_line
ORDER BY metric;

-- A failed foreign key load would have stopped the import. This check makes the
-- relationship visible to people learning the model.
SELECT
    COUNT(*) FILTER (WHERE p.stock_code IS NULL) AS missing_products,
    COUNT(*) FILTER (WHERE f.customer_id IS NOT NULL AND c.customer_id IS NULL) AS missing_customers
FROM retail.fact_sales_line AS f
LEFT JOIN retail.dim_product AS p ON p.stock_code = f.stock_code
LEFT JOIN retail.dim_customer AS c ON c.customer_id = f.customer_id;
