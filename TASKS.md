# Tasks

Work sequentially by default. Parallelise only substantial independent tasks without shared-file conflicts. Update checkboxes based on **verified** results; document blockers rather than claiming success.

- [x] **Record data discovery.** Preserve the results of the three-source Python test in [data discovery notes](docs/data-discovery.md).
- [ ] **1. Validate NHS inputs.** Check older files for availability, schema changes and revisions. Verify NHS metric definitions and Type 1 applicability. Record the decisions.
- [ ] **2. Verify the environment.** Set up Databricks Free Edition, a Volume and a small PySpark/Delta test. Check Jobs availability and try a Power BI Desktop Import connection to the Databricks SQL Warehouse. Use a CSV export if the connection fails.
- [ ] **3. Process one month end to end.** Build the first Bronze, Silver and Gold tables in PySpark and SQL. Check organisation-month keys and reconcile totals. Show one verified metric in Power BI.
- [ ] **4. Load and test the historical series.** Obtain monthly NHS releases from June 2023 onward. Preserve the source files and revision metadata. Check schemas, missing values, reruns and at least one revised-file scenario. Add ODS data if the join is useful and validated.
- [ ] **5. Orchestrate.** Create and execute a Databricks Job for the transformation stages. Document the manual input step.
- [ ] **6. Complete Power BI and verify the project.** Build the Overview, Organisation Comparison and Patient Flow pages. Validate displayed numbers and run an end-to-end check. Update the README with setup instructions, screenshots, test results, data caveats and a concise project description for a CV.

**Completion rule:** Actual successful runs and checked outputs matter more than adding features. Do not add forecasting, a web frontend or elaborate agent orchestration.
