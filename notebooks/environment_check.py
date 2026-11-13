# Databricks notebook source
"""Check serverless PySpark, a Unity Catalog volume and a managed Delta table."""

catalog = spark.sql("SELECT current_catalog()").first()[0]
if catalog in {"hive_metastore", "system", "samples"}:
    raise ValueError("Select a writable Unity Catalog catalog and run the notebook again.")

schema = "nhs_ed_environment_check"
catalog_sql = "`" + catalog.replace("`", "``") + "`"
schema_sql = f"{catalog_sql}.{schema}"
table_sql = f"{schema_sql}.smoke_test"
volume = f"/Volumes/{catalog}/{schema}/smoke_files"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_sql}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {schema_sql}.smoke_files")

probe_path = f"{volume}/probe.txt"
probe_text = "nhs-ed-pressure"
dbutils.fs.put(probe_path, probe_text, True)
if spark.read.text(probe_path).first()[0] != probe_text:
    raise RuntimeError("Volume readback failed.")
print(f"Volume write and read passed: {probe_path}")

expected = [(1, "ready"), (2, "ready")]
df = spark.createDataFrame(expected, "id INT, status STRING")
df.write.format("delta").mode("overwrite").saveAsTable(table_sql)
actual = [tuple(row) for row in spark.table(table_sql).orderBy("id").collect()]
if actual != expected:
    raise RuntimeError(f"Delta readback failed: {actual}")
print(f"Delta write and read passed: {table_sql}")
display(spark.table(table_sql).orderBy("id"))
