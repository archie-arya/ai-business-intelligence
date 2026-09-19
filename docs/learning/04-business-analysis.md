# Lesson 4: Build a trustworthy business analysis layer

## What we did

We separated analysis into two jobs:

| Layer | Responsibility |
|---|---|
| SQL | Define metrics at the correct data grain and retrieve them from PostgreSQL. |
| Python | Create charts and a readable narrative from the query results. |

Run the report:

```bash
source .venv/bin/activate
python scripts/build_business_report.py
```

It writes a Markdown summary and two charts to `reports/`. They are generated
outputs, so Git ignores them; the code and SQL that produce them are tracked.

## Why order grain matters

The fact table is at **sales-line** grain. If we calculated average order value
as `SUM(revenue) / COUNT(*)` on that table, we would get average line value,
not average order value. `004_monthly_kpis.sql` first aggregates lines to an
invoice total, then calculates order metrics.

## Why partial periods are dangerous

The source ends on 9 December 2011. Comparing that partial December with a
complete November would manufacture a false decline. The report visibly
excludes the final partial month from month-over-month commentary.

## A useful analysis discipline

Start with descriptive questions:

1. What changed? Revenue, orders, average order value, active customers.
2. Where did it change? Country, product, customer segment, time period.
3. Why might it have changed? This requires a decomposition or evidence—not a
   ranking presented as causality.

The later agent will be constrained to follow this same discipline.

## References

- [PostgreSQL aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Pandas user guide: visualisation](https://pandas.pydata.org/docs/user_guide/visualization.html)
- [Matplotlib quick start](https://matplotlib.org/stable/users/explain/quick_start.html)
