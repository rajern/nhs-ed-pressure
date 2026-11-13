# Architecture

## Data flow
1. **Source:** Monthly NHS England A&E CSVs; optional ODS organisation reference.
2. **Landing:** Python downloads files locally; manual upload to a Databricks Unity Catalog Volume is acceptable. Preserve original files and record source URL, reporting month, retrieval date, release/revision identifier and checksum.
3. **Bronze (Delta):** Ingest raw observations with source metadata; exclude nothing irreversibly.
4. **Silver (Delta):** Standardise types, validate keys, remove published total rows from organisation-level facts, resolve revisions deterministically and join reliable organisation metadata.
5. **Gold (Delta/SQL):** Provide Power BI-ready monthly facts and dimensions:
   - `fact_ae_monthly`: one row per reporting organisation and month (for the selected reporting scope), with verified metrics.
   - `dim_organisation`: stable identifier, name and verified attributes; handle unknown or changed codes explicitly.
   - `dim_date`: month, year, quarter and time-sort fields.
6. **Reporting:** Power BI Desktop connects to Databricks SQL Warehouse using **Import** if it works in this Free Edition account; otherwise export Gold data as CSV.

## Execution and guardrails
- Use Databricks Jobs for the Bronze → Silver → Gold transformations; raw-file upload may remain manual.
- Ensure idempotent processing and traceability to each NHS release. A newer revision must not silently create duplicate organisation-month rows.
- Distinguish **Type 1** metrics from admissions/delay metrics whose published scope may differ. Never silently combine incompatible populations or measures.
- Check actual CSV schemas and official NHS indicator definitions before settling exact column names, transformations and Power BI formulas.
- Keep the implementation simple and version-controlled. Document any limitations or Free Edition features that fail practical testing.

Official source: https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/
