CREATE SCHEMA IF NOT EXISTS retail;

DROP TABLE IF EXISTS retail.fact_sales_line CASCADE;
DROP TABLE IF EXISTS retail.dim_product CASCADE;
DROP TABLE IF EXISTS retail.dim_customer CASCADE;
DROP TABLE IF EXISTS retail.dim_calendar CASCADE;

CREATE TABLE retail.dim_product (
    stock_code TEXT PRIMARY KEY,
    product_name TEXT NOT NULL
);

CREATE TABLE retail.dim_customer (
    customer_id INTEGER PRIMARY KEY,
    country TEXT NOT NULL
);

CREATE TABLE retail.dim_calendar (
    calendar_date DATE PRIMARY KEY,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month TEXT NOT NULL,
    month_name TEXT NOT NULL
);

CREATE TABLE retail.fact_sales_line (
    sales_line_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL REFERENCES retail.dim_product(stock_code),
    description TEXT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    invoice_date TIMESTAMP NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    customer_id INTEGER REFERENCES retail.dim_customer(customer_id),
    country TEXT NOT NULL,
    line_revenue NUMERIC(14, 2) NOT NULL,
    order_date DATE NOT NULL REFERENCES retail.dim_calendar(calendar_date),
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month TEXT NOT NULL
);

CREATE INDEX fact_sales_line_invoice_idx ON retail.fact_sales_line(invoice_no);
CREATE INDEX fact_sales_line_date_idx ON retail.fact_sales_line(order_date);
CREATE INDEX fact_sales_line_product_idx ON retail.fact_sales_line(stock_code);
CREATE INDEX fact_sales_line_customer_idx ON retail.fact_sales_line(customer_id);
