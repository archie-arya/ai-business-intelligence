# Revenue Recognition Policy

## Purpose
Defines how revenue-related metrics should be interpreted in BI reporting.

## Revenue
Revenue represents the value of sales recognized from completed customer transactions. For BI reporting, revenue should normally be calculated from line-level sales data.

## Gross Revenue
Gross revenue is merchandise sales before deductions such as discounts, returns, and other adjustments.

## Net Revenue
Net revenue represents recognized sales after applicable discounts and returns. When a query says "revenue" without further qualification, use the standard BI definition of net recognized revenue unless the report specifies otherwise.

## Returns
Returned merchandise should reduce net revenue in the period in which the return is recognized.

## Discounts
Promotional discounts reduce realized selling price and should be considered when comparing gross and net revenue.

## Period Completeness
A reporting period must be checked for completeness before comparing it with other periods. A quarter containing only part of its final month should be labelled incomplete.

## BI Guidance
Use SQL for numerical revenue calculations. Use this document for business definitions and interpretation.
