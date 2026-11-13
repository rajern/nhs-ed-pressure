# Run the NHS history load as a Databricks Job

The job uses one Notebook task for the Bronze, Silver and Gold stages already tested in the [historical run](historical-run.md). Run it manually for the June 2023 to October 2026 snapshot. Prepare the bundle locally and upload it to the same catalog's `nhs_ed.raw` volume. The first job run can use the ZIP already uploaded for the historical run.

1. In Databricks, open **Jobs & Pipelines → Create → Job**. Name the job `NHS ED History Load`.
2. Choose **Notebook**. Enter `load_nhs_ed_history` as the task name, set **Source** to **Workspace**, and select the existing `history_pipeline` notebook for **Path**. Use **Serverless** compute and click **Save task**.
3. Click **Run now**. When the run finishes, open it under **Runs** and select the task. Confirm the status is **Succeeded** and the output includes both `Revision and rerun checks passed` and `History checks passed: 41 months, 8,112 Gold rows, 43 releases.` Record the run URL and result.

Use the default of one concurrent run. Start the job after the upload finishes and let the job finish before refreshing Power BI. If it reports that the ZIP is missing, compare the catalog in the reported volume path with the one used for the historical run. For an interrupted write, rerun with the same ZIP.

See the Databricks guides for [Notebook tasks](https://docs.databricks.com/aws/en/jobs/tasks/notebook) and [Run now](https://docs.databricks.com/aws/en/jobs/run-now).

The workspace owner confirmed that the manual job run succeeded. The project records the expected validation output above.
