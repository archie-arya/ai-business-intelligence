# BI Business Data Dictionary

## Revenue
Business measure representing recognized sales value. The precise calculation depends on the metric requested and the revenue policy.

## Order
A customer transaction that may contain one or more line items.

## Sales Line
A line-level record representing a product within an order. Line-level data is generally the appropriate grain for aggregating product sales.

## Product
An item offered for sale.

## Customer
An entity associated with one or more orders.

## Quantity
The number of units represented by a sales line.

## Unit Price
The price associated with one unit. Whether it is before or after adjustments depends on the database field definition.

## Line Revenue
Revenue attributable to a sales line. The database schema is the source of truth for the actual stored field and its calculation.

## Date
The date associated with the relevant business event. Time-based questions should use the appropriate date field rather than assuming all date columns represent the same event.

## Agent Guidance
The database schema is authoritative for available fields and numerical values. This dictionary supplies contextual information. Never fabricate unavailable fields or definitions.
