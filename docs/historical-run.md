# Load the NHS historical series

The bundle covers June 2023 through October 2026. It contains 41 CSVs selected by the NHS monthly indices and the superseded originals for June 2023 and July 2024. The ZIP preserves the original file bytes. Its manifest records exact CSV and index URLs, NHS link labels, reporting months, selected versions, checksums and retrieval time. Release dates are recorded where explicitly established, including dates in NHS revision labels and the October 2026 publication date. Other release dates are null.

## Prepare and run

1. From the project root, run `python scripts/prepare_nhs_history.py` to download and validate the files and build `data/nhs-ae-history.zip`. The data directory is ignored by Git.
2. In Databricks, create the `nhs_ed` schema and the `raw` volume in your writable Unity Catalog catalog if needed. The setup cell in [october_2026_pipeline.py](../notebooks/october_2026_pipeline.py) does this for the current catalog. Use **Workspace → ⋮ → Import** to import [history_pipeline.py](../notebooks/history_pipeline.py). Upload the ZIP itself through **Catalog → your catalog → nhs_ed → raw → Upload to this volume**.
3. Open the notebook and select **Run all**. It should print `Revision and rerun checks passed` followed by `History checks passed: 41 months, 8,112 Gold rows, 43 releases.` The monthly summary should show 191 organisations and 60.1% within four hours for October 2026.
4. In the existing Power BI Desktop report, select **Home → Refresh**. Use the `reporting_month` field to confirm both June 2023 and October 2026 are available. Filter to October 2026 to check that the card still shows 60.1%. Save the report.

## Source checks

| Check | Result |
| --- | --- |
| Releases and row counts | 43 CSVs and 8,554 Bronze records including national totals. 8,112 distinct organisation-month rows across the 41 selected releases. |
| Required identifiers and counts | No blanks, invalid counts or duplicate organisation codes within a release. All 18 published count columns reconcile to the England total in every file. |
| September 2024 | Six extra CSV columns had empty data cells. The pipeline checks they are empty before omitting them from the staged records. The original CSV is preserved. |
| February 2026 | The England total uses the month in its period field. The pipeline accepts this specific variant and still reconciles the total. |
| June 2023 revision | Organisation coverage increases from 202 to 204 with `G0Q0L` and `K6K0R` added. |
| July 2024 revision | Organisation coverage increases from 197 to 198 with `AD913` added. |

Sources are the [NHS monthly series](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/) and its four fiscal-year indices. The [September 2024 CSV](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2024/10/Monthly-AE-September-2024.csv) contains the extra columns.

## Writes and verification

Bronze keeps each release by month and SHA-256. Silver and Gold replace the covered months with the versions selected in the manifest, using [Delta selective overwrite](https://docs.databricks.com/aws/en/delta/selective-overwrite). Before publishing, a disposable Delta table tests the original June release, its replacement and a repeated replacement, with October as a control. After writing, the notebook checks Bronze release counts and reconciles each persisted Silver and Gold month to its source. If a run stops between table writes, rerun the same bundle before refreshing Power BI.

The full notebook logic passed two consecutive local runs with PySpark 4.0.1 and Delta Lake 4.0.0, starting from copies of the October tables. Both runs kept 8,554 Bronze rows and 8,112 Gold rows and returned 60.1% for October. Both revision checks replaced the original June rows with the revised set and left October unchanged.

The workspace owner confirmed the Databricks history run and Power BI refresh checks. Organisation names and parent organisations reflect each monthly release. The optional ODS enrichment and separate reporting dimensions remain open. Use the [job runbook](databricks-job.md) to run the same pipeline through Lakeflow Jobs.
