-- Countries ordered by gross revenue, including their share of total revenue.
WITH country_revenue AS (
    SELECT country, SUM(line_revenue) AS revenue
    FROM retail.fact_sales_line
    GROUP BY country
)
SELECT
    country,
    ROUND(revenue, 2) AS revenue,
    ROUND(100 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct
FROM country_revenue
ORDER BY revenue DESC;
