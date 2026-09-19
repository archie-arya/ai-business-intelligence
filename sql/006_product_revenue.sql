-- Products ordered by revenue. Product labels come from dim_product so each
-- stock code is represented once despite source-description inconsistencies.
SELECT
    p.stock_code,
    p.product_name,
    ROUND(SUM(f.line_revenue), 2) AS revenue,
    SUM(f.quantity) AS units_sold
FROM retail.fact_sales_line AS f
JOIN retail.dim_product AS p USING (stock_code)
GROUP BY p.stock_code, p.product_name
ORDER BY revenue DESC
LIMIT 15;
