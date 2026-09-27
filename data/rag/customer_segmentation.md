# Customer Segmentation Guide

## New Customer
A customer whose first recorded purchase occurs during the analysis period.

## Returning Customer
A customer who purchased before the current analysis period and purchases again during it.

## High-Value Customer
A customer whose cumulative net revenue places them in the company's high-value segment. Do not assume a threshold; retrieve the current business rule if one is required.

## Inactive Customer
A previously active customer with no purchase activity during the defined inactivity window.

## Analytical Guidance
"New customers this quarter" and "new customers ever" are different questions because the time window changes the definition.

The agent should retrieve numerical customer metrics from PostgreSQL. This document provides definitions, not numerical answers.

## Important
Never invent customer-segment thresholds.
