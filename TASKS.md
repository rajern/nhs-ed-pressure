# Tasks

Work sequentially by default. Parallelise only substantial independent tasks without shared-file conflicts. Update checkboxes based on **verified** results; document blockers rather than claiming success.

- [x] **Record data discovery.** Preserve the results of the three-source Python test in [data discovery notes](docs/data-discovery.md).
- [x] **1. Validate NHS inputs.** Check older files for availability, schema changes and revisions. Verify NHS metric definitions and Type 1 applicability. See the [validation notes](docs/nhs-input-validation.md).
- [x] **2. Verify the environment.** The Volume and PySpark/Delta checks passed in Databricks Free Edition, the Job creation option was available, and Power BI Desktop imported both test rows from the SQL warehouse. See the [environment check](docs/environment-check.md).
- [x] **3. Process one month end to end.** The October 2026 run produced 191 organisation-month rows in Gold, and Power BI showed 60.1% of Type 1 attendances within four hours. See the [run notes](docs/october-2026-run.md).
- [x] **4. Load and test the historical series.** The workspace owner confirmed the Databricks history run and Power BI refresh checks. Local Delta runs verified reruns and a revised-file replacement. See the [historical run guide](docs/historical-run.md).
- [x] **5. Orchestrate.** The workspace owner confirmed the serverless history job succeeded. See the [job runbook](docs/databricks-job.md) for the manual upload and run steps.
- [x] **6. Complete Power BI and verify the project.** Built and checked Overview, Organisation Comparison and Patient Flow. The report refreshed from Databricks and matched the NHS reference figures. See the [report checks](docs/power-bi-report.md) and the [README](README.md).

**Completion rule:** Actual successful runs and checked outputs matter more than adding features. Do not add forecasting, a web frontend or elaborate agent orchestration.
