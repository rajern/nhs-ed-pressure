# Run October 2026 end to end

Use the original [October 2026 NHS CSV](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/October-2026-CSV-WD35qg.csv). Keep its filename and bytes unchanged. The notebook checks its SHA-256 against the release validated in [NHS input validation](nhs-input-validation.md).

1. In Databricks, import [october_2026_pipeline.py](../notebooks/october_2026_pipeline.py) using **Workspace → ⋮ → Import**. Open the notebook and run the setup cell that starts with `catalog = ...`. It creates the project schema and raw Volume in the current catalog.
2. In **Catalog**, open that catalog, then **nhs_ed → raw**. Use **Upload to this volume** to upload the CSV. Return to the notebook and select **Run all**.
3. Check the output. Bronze preserves 192 raw records, including the published England total. Silver validates and reconciles all 18 count columns, then keeps 191 unique organisation-month rows. Gold exposes the Type 1 counts for those organisations. The notebook reads back Gold and checks the values below.
4. In Power BI Desktop, use **Get data → Databricks → Import** with the warehouse connection that passed the [environment check](environment-check.md). In Navigator, select **nhs_ed → fact_ae_monthly** in the catalog printed by the notebook, then **Load**.
5. In Power BI, select **New measure** and replace the entire default formula with the DAX below. Format it as **Percentage** with one decimal place. Add it to a **Card** on a clean page and check that it shows **60.1%**. If the report contains other months later, filter the page to October 2026 for this check.

```dax
Type 1 Within 4 Hours % =
DIVIDE(
    SUM(fact_ae_monthly[type_1_within_4h]),
    SUM(fact_ae_monthly[type_1_attendances])
)
```

| October 2026 reference | Expected |
| --- | ---: |
| Organisation-month rows | 191 |
| Type 1 attendances | 1,548,280 |
| Type 1 attendances over four hours | 617,001 |
| Type 1 attendances within four hours | 931,279 |
| Type 1 within four hours | 60.1% |
| Emergency admissions via Type 1 | 408,428 |

The local PySpark check matched these values and rejected a duplicate organisation, an invalid count and a mismatched England total. The workspace owner confirmed that the Databricks notebook returned the expected result and the Power BI card displayed 60.1%.

Rerun the notebook on the same file to check that Gold still shows 191 rows. The notebook replaces the matching release in Bronze and the matching month in Silver and Gold. The three writes are separate Delta transactions. If a run stops during publishing, rerun it with the same input before refreshing Power BI.

This run uses one source release and a single Gold fact table. Organisation and date attributes are included in the fact for the first Power BI check. Use the [historical run](historical-run.md) to extend the fact with older months and their revisions.
