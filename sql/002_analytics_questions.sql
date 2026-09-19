-- These are baseline questions with deterministic answers.
-- Run them before introducing an LLM so we have a correctness oracle.

-- Q1: Revenue by quarter
SELECT year, quarter, ROUND(SUM(line_revenue), 2) AS revenue
FROM retail.fact_sales_line
GROUP BY year, quarter
ORDER BY year, quarter;

-- Q2: Top 10 products by revenue
SELECT p.stock_code, p.product_name, ROUND(SUM(f.line_revenue), 2) AS revenue
FROM retail.fact_sales_line AS f
JOIN retail.dim_product AS p USING (stock_code)
GROUP BY p.stock_code, p.product_name
ORDER BY revenue DESC
LIMIT 10;

-- Q3: Revenue by country, excluding the United Kingdom
SELECT country, ROUND(SUM(line_revenue), 2) AS revenue
FROM retail.fact_sales_line
WHERE country <> 'United Kingdom'
GROUP BY country
ORDER BY revenue DESC;
