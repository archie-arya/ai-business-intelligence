# Lesson 1: Build the data foundation

## What we did

We inspected the supplied UCI Online Retail workbook and built a deterministic
preparation script. The raw workbook stays unchanged. The script creates:

- `fact_sales_line`: one valid, non-cancelled sales line per source row.
- `dim_product`: one product row per stock code.
- `dim_customer`: customers that have a customer ID in the source.
- `dim_calendar`: one row per day in the sales period.
- `audit_metrics`: counts and revenue used to check the transformation.

Run it with:

```bash
python scripts/prepare_data.py
python scripts/validate_data.py
```

## Cleaning decisions

1. Exact duplicate rows are removed.
2. Invoice numbers beginning with `C` are treated as cancellations.
3. Cancellations and non-positive quantities are excluded from the sales fact.
4. A missing customer ID remains missing; it is not guessed.
5. Product labels are selected by most frequent non-null description per stock
   code. This prevents a changing description from multiplying products.

These rules are assumptions, not universal truths. Later we can model returns
as a separate fact if the business question requires net revenue.

The validation script is our first correctness oracle. It checks that fact rows
obey the business rules and that dimension keys resolve. It also prints a few
answers that we will reproduce in SQL.

## Concepts to learn

### Grain

The grain of `fact_sales_line` is one invoice/product line. Every metric must
respect that grain. For example, revenue is `quantity * unit_price` summed over
lines; it is not the sum of invoice totals repeated on every line.

### Star schema

The fact table stores measurable events. dimensions provide descriptive context.
This makes common questions straightforward and gives the future agent a small,
inspectable schema.

### Data contract

The SQL constraints encode expectations such as positive quantity, non-negative
price, and valid dimension references. Constraints turn silent data corruption
into an observable load failure.

## Reference material

- [UCI Online Retail dataset documentation](https://archive.ics.uci.edu/dataset/352/online%2Bretail)
- [PostgreSQL `CREATE TABLE`](https://www.postgresql.org/docs/current/sql-createtable.html)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

## Exercises

1. Explain why `customer_id` must remain nullable in this dataset.
2. Write a SQL query for average order value. First decide whether an order is
   an invoice number and explain how you avoid counting each line as an order.
3. Decide whether cancellations should be excluded, represented as negative
   revenue, or modeled separately. Write down what each choice means.
