# NHS Emergency Department Pressure

A data engineering project exploring patient demand, waiting times and admission delays across NHS England's **Type 1 emergency departments**.

## Questions
- How do attendances and waiting times change over time?
- How does performance differ between reporting organisations?
- Where do admission delays indicate pressure on patient flow?

## Data and approach
- **Source:** Monthly NHS England A&E CSV files, from June 2023 onwards; NHS organisation data where useful.
- **Pipeline:** Manual raw-file upload → Databricks Free Edition → Bronze / Silver / Gold Delta tables using PySpark and SQL.
- **Orchestration:** Databricks Jobs for the transformation pipeline.
- **Reporting:** Power BI Desktop (Databricks Import connection if available; CSV export as fallback).

The dashboard will cover **Overview**, **Organisation Comparison** and **Patient Flow**. Findings will describe patterns and associations, not claim causal explanations.

## Status
Source discovery is complete for three sample months. See the [data discovery notes](docs/data-discovery.md) for the evidence and [tasks](TASKS.md) for the next checks. The first implementation milestone is to process one month and verify a metric in Power BI before loading the historical series.
