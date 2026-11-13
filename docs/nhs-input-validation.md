# NHS input validation

The Monthly A&E Attendances and Emergency Admissions CSV supports reporting-organisation comparisons of Type 1 demand, four-hour performance and emergency admissions via Type 1. The decision-to-admit delay columns cover A&E admissions without a department-type breakdown.

## Coverage and CSV checks

On 13 November 2026, the four NHS fiscal-year indices listed a monthly CSV for every month from June 2023 to October 2026 (41 months). NHS England resumed including four-hour performance from 14 trial trusts in June 2023, which supports using that month as the start of this project. The indices establish link coverage. The seven downloads below establish file-level checks for the sample. [2023–24](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2023-24/) · [2024–25](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2024-25/) · [2025–26](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2025-26/) · [2026–27](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2026-27/) · [Impact of the field trial](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2023/07/Impact-of-CRS-on-national-AE-timeseries.pdf)

| Reporting month | CSV releases downloaded | Organisation rows |
| --- | --- | ---: |
| June 2023 | [Original](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2023/07/Monthly-AE-June-2023.csv) · [Revised 13 June 2024](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2024/06/June-2023-revised-130624-ndcvf47.csv) | 202 → 204 |
| July 2024 | [Original](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2024/08/Monthly-AE-July-2024.csv) · [Revised 14 November 2024](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2024/11/Monthly-AE-July-2024-revised.csv) | 197 → 198 |
| March 2026 | [Revised 14 May 2026](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/05/Monthly-AE-March-2026-revised-flkg42.csv) | 199 |
| April 2026 | [Revised 12 November 2026](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/April-2026-Revised-12.11.26-CSV-28KB-aW27FD.csv) | 190 |
| October 2026 | [Original](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/October-2026-CSV-WD35qg.csv) | 191 |

All seven files shared the same 22 headers and read as comma-separated UTF-8. Organisation codes were unique within each release. Identifiers and counts were populated, the counts were non-negative integers, and all 18 provider measure sums matched the published England total. June 2023 and July 2024 revisions used \`Total\` where other samples used \`TOTAL\`. Trim identifiers and match the total marker case-insensitively. Validate and retain the published total separately from the organisation facts.

## Handling revisions

The June 2023 revision added two organisations, changed counts for four existing organisations, added 4,772 unplanned attendances at other A&E departments and reduced the national 12-hour decision-to-admit count by 43. The July 2024 revision added one organisation and changed counts for one existing organisation. The project should retain the raw releases with the official release or revision date, source URL and checksum. Silver should select the latest verified release and replace the **whole reporting month**, so the set of organisations also comes from that release. Use the official release order when an older file is retrieved after a revision. [NHS revisions policy](https://www.england.nhs.uk/statistics/code-compliance/#Unifypolicy)

## Metric decisions

| Measure | Definition and scope for the project |
| --- | --- |
| Type 1 attendances | Add the Type 1 unplanned count and the attended Type 1 booked appointments. |
| Type 1 attendances over four hours | Add the Type 1 over-four-hour counts for unplanned and booked attendances. The attendance clock runs to admission, transfer or discharge. NHS guidance specifies how booked visits start the clock. |
| Type 1 four-hour performance | Divide total Type 1 attendances minus Type 1 attendances over four hours by total Type 1 attendances. Return blank for a zero denominator. Across organisations or months, sum the counts before dividing. |
| Emergency admissions via Type 1 | Use \`Emergency admissions via A&E - Type 1\`. It counts emergency admissions via Type 1 to the same provider. Keep it as a separate count. |
| Admission delays after the decision to admit | The 4–12 hour and 12+ hour counts have no Type 1 breakdown in these CSVs. Omit them from Type 1 measures. If the Patient Flow page includes them later, label the scope as **all A&E types** and identify the decision-to-admit clock. |

The NHS collection guidance defines the source measures. NHS England also publishes a separate 12-hour measure from arrival using ECDS. From April 2026 the Acute Provider Table uses an acute trust footprint for its four-hour measure. Use the monthly CSV and its statistical commentary to validate the provider-level Type 1 calculation in this project. [NHS collection guidance](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2020/08/AE-Attendances-Emergency-Definitions-v5.0-final-August-2020.pdf) · [Acute Provider Table methodology](https://data.england.nhs.uk/about)

## Reference for the first end-to-end run

Use October 2026 for the first Databricks-to-Power BI run. The CSV gives **1,548,280** Type 1 attendances, of which **617,001** exceeded four hours. That leaves **931,279** within four hours (**60.1%**), matching the NHS commentary. The CSV gives **408,428** emergency admissions via Type 1. It also matches the commentary's **57,840** waits over 12 hours after the decision to admit across A&E types. [October 2026 statistical commentary, page 2](https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/Statistical-commentary-October-2026-DW43tf-1.pdf)

Run `python scripts/validate_nhs_inputs.py` from the repository root to repeat the sample checks and print the source URLs, SHA-256 checksums, revision differences and October reference values. It uses the Python standard library and downloads its inputs directly. Validate every file during the historical load.
