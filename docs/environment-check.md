# Verify the Databricks and Power BI environment

1. In Databricks, open **Workspace**. Open the folder menu and choose **Import**, then select [environment_check.py](../notebooks/environment_check.py). Open the imported notebook and select **Run all** using Serverless compute. It should print success messages for the volume and the Delta table, then display two rows with status `ready`. The notebook writes to a dedicated `nhs_ed_environment_check` schema in the current catalog.
2. Open **Jobs & Pipelines**, click **Create**, and check that **Job** appears in the menu. Creating the pipeline job is a later task. [Databricks Jobs guide](https://docs.databricks.com/aws/en/jobs/jobs-quickstart)
3. In **SQL Warehouses**, open the existing warehouse and find **Server hostname** and **HTTP Path** under **Connection details**. In Power BI Desktop, select **Get data**, search for **Databricks**, enter both values, and choose **Import**. Use **OAuth → Sign in** if offered. In Navigator, open the catalog printed by the notebook, select `nhs_ed_environment_check.smoke_test`, and choose **Load**. Verify that both rows appear in Power BI. [Databricks Power BI connection guide](https://docs.databricks.com/aws/en/partners/bi/power-bi/desktop)

The workspace owner confirmed that the Volume and Delta checks passed, the **Job** option appeared under **Create**, and Power BI Desktop imported both `ready` rows directly from the Serverless Starter Warehouse. The project can use direct Import for the first monthly run.

If direct import fails, run the SQL below in Databricks. Replace `<catalog>` with the catalog from the notebook output. Download the query results as CSV, then open them in Power BI Desktop via **Get data → Text/CSV**. Verify that both rows appear.

```sql
SELECT id, status
FROM `<catalog>`.nhs_ed_environment_check.smoke_test
ORDER BY id;
```
