# Lesson 3: Load a warehouse into PostgreSQL

## What we are building

The project now has a local PostgreSQL database named `retail_bi`. The database
owns the queryable copy of the curated data; the CSV files remain a reproducible
load artifact.

## Run the load

```bash
source .venv/bin/activate
python scripts/prepare_data.py
python scripts/load_postgres.py
psql -d retail_bi -f sql/002_analytics_questions.sql
```

`load_postgres.py` deliberately uses PostgreSQL's `psql` and `\\copy` rather
than a Python ORM. At this stage we want the loading mechanism to be explicit:

1. Create tables and constraints.
2. Load dimensions first, because the fact table references them.
3. Load the sales-line fact table.
4. Run `ANALYZE`, which updates the planner's statistics.
5. Run quality checks and compare their results with Python.

## Key concept: referential integrity

`fact_sales_line.stock_code` references `dim_product.stock_code`. This means
PostgreSQL rejects a sale whose product does not exist. It is one of the ways a
database protects analytical correctness.

## Key concept: indexes

The schema indexes invoice, date, product, and customer columns because we
expect our analysis and later agent questions to filter or join on them. We do
not add every possible index: each one also has a write and storage cost.

## References

- [PostgreSQL `COPY` documentation](https://www.postgresql.org/docs/current/sql-copy.html)
- [PostgreSQL `ANALYZE` documentation](https://www.postgresql.org/docs/current/sql-analyze.html)
- [PostgreSQL query planning documentation](https://www.postgresql.org/docs/current/using-explain.html)
