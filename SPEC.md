# Project specification

## Goal
Build a reproducible data pipeline and Power BI report exploring **NHS England Type 1 emergency department pressure**: demand, four-hour performance, differences between organisations and admission delays.

## Scope
- Monthly NHS A&E CSVs from **June 2023 to the latest available month**; retain and handle revised releases.
- Focus comparisons on **Type 1** attendances and four-hour performance. Do not attribute all-type admission measures to Type 1 unless NHS definitions support it.
- Optional NHS ODS organisation lookup when it improves reliable comparisons.
- Databricks Free Edition, PySpark, SQL, Delta Lake (Bronze/Silver/Gold), Databricks Jobs and Power BI Desktop.
- Raw files may be uploaded manually. No predictive model, web app or paid infrastructure.

## Questions and report
Three Power BI pages: **Overview**, **Organisation Comparison**, **Patient Flow**.

Proposed measures: Type 1 attendances; Type 1 four-hour performance; visits over four hours (only if correctly derivable); emergency admissions; 12-hour admission delays; month-on-month/year-on-year change. **Before implementing, verify NHS definitions, units, denominators and whether admissions/delays are Type 1-specific.** Clearly label or omit metrics that cannot support the chosen scope. Avoid causal claims or unsupported organisation rankings.

## Done when
- Historical data can be processed reproducibly into tested Bronze, Silver and Gold Delta tables.
- Re-runs do not duplicate records; revised files update the correct reporting period while keeping source provenance.
- Data quality checks cover schema, keys, missing values and reconciliation with NHS totals where applicable.
- A Databricks Job runs the transformation pipeline; Power BI displays a working report using Gold data (direct Import connection preferred, CSV fallback).
- GitHub contains code, tests, a usable README, dashboard screenshots and an honest record of limitations and any manual steps.

The [data discovery notes](docs/data-discovery.md) record the initial checks on three sample months. Validate the full historical data as part of the project.
