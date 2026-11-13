# Power BI report

Open [nhs-ed-pressure.pbip](../powerbi/nhs-ed-pressure.pbip) in Power BI Desktop. Set the values below through **Home → Transform data → Edit parameters**. In Databricks, the **Connection details** tab of the SQL warehouse shows the hostname and HTTP path. Set the catalog to the one containing `nhs_ed.fact_ae_monthly`.

| Parameter | Warehouse detail |
| --- | --- |
| `DatabricksHost` | Server hostname |
| `DatabricksHttpPath` | HTTP path |
| `DatabricksCatalog` | Catalog name |

Apply the parameter changes, sign in to Databricks if prompted, then refresh the model. The public project files contain the report and model definitions. The local PBIX and Power BI caches contain the imported data and are ignored by Git. [Power BI parameters](https://learn.microsoft.com/en-us/power-query/power-query-query-parameters) · [Databricks Power BI connection](https://docs.databricks.com/aws/en/partners/bi/power-bi/desktop)

## Desktop checks

The final report was opened and refreshed from the Databricks SQL warehouse. The parameterized project also refreshed successfully in a test copy configured for the project warehouse. The monthly and regional filters were checked against the original NHS CSV counts.

| Selection | Attendances | Over four hours | Within four hours | Emergency admissions |
| --- | ---: | ---: | ---: | ---: |
| England, October 2026 | 1,548,280 | 617,001 | 60.1% | 408,428 |
| England, June 2023 | 1,389,009 | 553,299 | 60.2% | 381,815 |
| London, June 2023 | 227,425 | 88,427 | 61.1% | 53,095 |

The October year-over-year attendance change is **+4.5%**, based on the 1,481,222 attendances in October 2025. Select a single month on **Organisation Comparison** when comparing providers. Four-hour performance divides the total within four hours by total Type 1 attendances in the selected population. Emergency admissions are reported via Type 1. See [NHS metric definitions and caveats](nhs-input-validation.md#metric-decisions).
