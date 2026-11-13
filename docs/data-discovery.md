# Data discovery

On 13 November 2026, we downloaded and profiled samples from three public health data sources in Python. We chose NHS England for the project because it publishes monthly files and revisions, which give us a way to test recurring ingestion, reconciliation and revision handling. The samples are small enough to run locally. Databricks and PySpark are part of the learning objective.

| Source | What the sample showed | What to carry forward |
| --- | --- | --- |
| NHS England A&E | The August, September and October 2026 files each had 191 reporting organisations and one England total row. All three had the same 22 columns. The organisation-month keys were unique, there were no blank cells, and organisation counts reconciled to the published totals for every measure column. A lookup for ODS code `RVV` matched all three files. | Track releases by reporting month and source version. Keep the published total for checks and exclude it from organisation-level facts. Check organisation changes before making comparisons over time. |
| Statistics Norway (SSB) | Three API extracts for 2023–2025 contained 15,804 rows across capacity and activity, staffing, and costs. The share of values marked `.` or `..` ranged from about 25% to 55% by extract. Beds, staffing and costs matched for 83 of 84 tested somatic organisation-year keys with a numeric bed count. | Suitable for a separate project on Norwegian hospital capacity. Preserve missing-value codes and keep national, regional and organisation totals at their own levels. |
| Norwegian waiting times | The public FHI activity API returned 810 values. The 90 missing values were all for full-year 2026. Python also extracted 10 national rows from an FHI publication and four national deadline-breach percentages from Norwegian Directorate of Health publications. | Automated activity retrieval worked. A repeatable download of the detailed waiting-time and deadline-breach series remains unverified. The NKI export view showed 305 filtered rows, but the CSV export produced no verifiable file. |

## What to verify next

- Compare older NHS files with the 2026 sample and find a reporting month with both original and revised files available.
- Verify the Type 1 four-hour denominator and the scope of admissions and admission-delay columns. Time spent in A&E and time from decision to admit measure different intervals.
- Run one month from raw CSV through Databricks to Power BI before loading the historical series.

## Sources and sample files

- NHS England A&E publications and original sample CSVs. [Release page](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2026-27/) · [August 2026, revised](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/August-2026-Revised-12.11.26-CSV-28KB-Pq49Sq.csv) · [September 2026](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/10/September-2026-CSV-Re72Eh.csv) · [October 2026](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/October-2026-CSV-WD35qg.csv) · [ODS lookup](https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/RVV)
- SSB Statbank tables. [Capacity and activity, 13942](https://www.ssb.no/en/statbank/table/13942/) · [Staffing, 13954](https://www.ssb.no/en/statbank/table/13954/) · [Costs, 14022](https://www.ssb.no/en/statbank/table/14022/)
- Norwegian activity and waiting-time publications. [FHI activity API, table 517](https://statistikk-data.fhi.no/api/open/v1/npr/Table/517/metadata) · [FHI waiting-time publication](https://www.fhi.no/nyheter/2026/aktivitet-og-ventetid-i-spesialisthelsetjenesten-ved-utgangen-av-august-2026/) · [Norwegian Directorate of Health NKI export](https://www.helsedirektoratet.no/statistikk/kvalitetsindikatorer/eksport-av-data-fra-de-nasjonale-kvalitetsindikatorene-nki)

The original discovery script, download manifest, profiling output and raw samples are retained in a local archive.
