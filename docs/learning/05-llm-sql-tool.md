# Lesson 5: Give an LLM a safe SQL tool

## The architecture

```text
Question → LLM generates SQL → guard validates it → PostgreSQL executes it
         → LLM explains returned rows → answer
```

This is not a fully autonomous agent yet. It is intentionally one bounded
tool-use round so that we can inspect each decision.

Run it with:

```bash
source .venv/bin/activate
python -m bi_agent.cli --show-sql "What were the top five countries by revenue?"
```

The default local model is `llama3:latest`. It was selected after a live
comparison found that the smaller installed `llama3.2:latest` reliably emitted
JSON but produced invalid SQL for a baseline question. Model choice is a
measurable engineering decision, not a branding decision.

## The safety boundary

The model never receives database credentials and cannot execute arbitrary
shell commands. Its SQL passes through two defences:

1. An allowlist accepts one `SELECT` or `WITH ... SELECT` statement only.
2. PostgreSQL executes it in a read-only transaction with a five-second timeout.

If PostgreSQL rejects otherwise allowed SQL, the prototype gives the database
error back to the model for one corrected attempt. A second failure stops the
workflow. This is the smallest useful example of **tool-feedback repair**.

Results are capped at 200 rows. This is not a complete production security
system, but it is a strong learning baseline. A production version would add a
database role with `SELECT` privileges only, query-cost limits, audit logs,
parameterisation where applicable, and an approval path for sensitive data.

## Why the schema contract matters

LLMs do not infer the meaning of an invoice, gross revenue, or an incomplete
month reliably. `bi_agent/schema.py` gives the model the table grain, joins,
and business definitions. A good tool description is part of the product—not
boilerplate.

## Evaluation exercise

Ask these questions and compare generated SQL with `sql/` baselines:

1. `What was revenue by quarter?`
2. `What were the top five countries by gross revenue?`
3. `What was average order value in November 2011?`

For each answer, inspect whether it uses `SUM(line_revenue)`, counts distinct
invoices for orders, and excludes incomplete December from a monthly comparison.
For quarter-level answers, it must also include the year; Q4 2010 and Q4 2011
are distinct periods and must never be added together.

### Join completeness matters

`customer_id` is missing on some valid sales rows. Joining `fact_sales_line` to
`dim_customer` with an inner join therefore drops revenue. Country is available
directly in the fact table, so country-revenue queries must group by
`fact_sales_line.country`. This is a common BI failure mode: a query can be
valid SQL and still undercount due to an inappropriate join.

## References

- [Ollama API reference](https://docs.ollama.com/api)
- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
