# Databricks notebook source
"""Load the validated October 2026 NHS release into Unity Catalog Delta tables."""

import csv
import hashlib
import io
from datetime import date
from pathlib import Path

from pyspark.sql import functions as F

SOURCE_FILE = "October-2026-CSV-WD35qg.csv"
SOURCE_URL = "https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/11/" + SOURCE_FILE
SOURCE_SHA256 = "9ca5df7770c8f28652b31eeaba92fafdb3eb0e215ee28aa906da2c7fdb99d253"
RELEASE_DATE = date(2026, 11, 12)
REPORTING_MONTH = date(2026, 10, 1)
SOURCE_PERIOD = "MSITAE-OCTOBER-2026"

# Map the published headings to Delta-safe column names.
SOURCE_COLUMNS = (
    ("Period", "source_period"),
    ("Org Code", "organisation_code"),
    ("Parent Org", "parent_organisation"),
    ("Org name", "organisation_name"),
    ("A&E attendances Type 1", "unplanned_type_1"),
    ("A&E attendances Type 2", "unplanned_type_2"),
    ("A&E attendances Other A&E Department", "unplanned_other"),
    ("A&E attendances Booked Appointments Type 1", "booked_type_1"),
    ("A&E attendances Booked Appointments Type 2", "booked_type_2"),
    ("A&E attendances Booked Appointments Other Department", "booked_other"),
    ("Attendances over 4hrs Type 1", "unplanned_over_4h_type_1"),
    ("Attendances over 4hrs Type 2", "unplanned_over_4h_type_2"),
    ("Attendances over 4hrs Other Department", "unplanned_over_4h_other"),
    ("Attendances over 4hrs Booked Appointments Type 1", "booked_over_4h_type_1"),
    ("Attendances over 4hrs Booked Appointments Type 2", "booked_over_4h_type_2"),
    ("Attendances over 4hrs Booked Appointments Other Department", "booked_over_4h_other"),
    ("Patients who have waited 4-12 hs from DTA to admission", "all_ae_dta_4_to_12h"),
    ("Patients who have waited 12+ hrs from DTA to admission", "all_ae_dta_over_12h"),
    ("Emergency admissions via A&E - Type 1", "emergency_admissions_via_type_1"),
    ("Emergency admissions via A&E - Type 2", "emergency_admissions_via_type_2"),
    ("Emergency admissions via A&E - Other A&E department", "emergency_admissions_via_other"),
    ("Other emergency admissions", "emergency_admissions_other_routes"),
)
RAW_HEADERS, COLUMN_NAMES = map(tuple, zip(*SOURCE_COLUMNS))
IDENTIFIERS = COLUMN_NAMES[:4]
COUNT_COLUMNS = COLUMN_NAMES[4:]
METRIC_COLUMNS = (
    "type_1_attendances",
    "type_1_over_4h",
    "type_1_within_4h",
    "emergency_admissions_via_type_1",
)
EXPECTED_TOTALS = (1_548_280, 617_001, 931_279, 408_428)


def read_release(spark, path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("The file does not match the validated October 2026 release.")

    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    if tuple(next(reader, ())) != RAW_HEADERS:
        raise ValueError("The NHS CSV headers do not match the expected schema.")
    for line, row in enumerate(reader, start=2):
        if len(row) != len(RAW_HEADERS):
            raise ValueError(f"Unexpected column count on CSV record {line}.")

    return (
        spark.read.option("header", True)
        .option("mode", "FAILFAST")
        .option("multiLine", True)
        .option("escape", '"')
        .csv(str(path))
        .toDF(*COLUMN_NAMES)
        .withColumn("reporting_month", F.lit(REPORTING_MONTH))
        .withColumn("source_url", F.lit(SOURCE_URL))
        .withColumn("source_sha256", F.lit(SOURCE_SHA256))
        .withColumn("source_release_date", F.lit(RELEASE_DATE))
    )


def to_silver(bronze):
    clean = bronze
    for name in IDENTIFIERS:
        clean = clean.withColumn(name, F.trim(F.col(name)))
    for name in ("source_period", "organisation_code"):
        clean = clean.withColumn(name, F.upper(F.col(name)))

    for name in COUNT_COLUMNS:
        clean = clean.withColumn(name, F.expr(f"try_cast(trim({name}) AS BIGINT)"))

    invalid = F.lit(False)
    for name in IDENTIFIERS:
        invalid = invalid | F.col(name).isNull() | (F.col(name) == "")
    for name in COUNT_COLUMNS:
        invalid = invalid | F.col(name).isNull() | (F.col(name) < 0)
    for visits, delayed in zip(COUNT_COLUMNS[:6], COUNT_COLUMNS[6:12]):
        invalid = invalid | (F.col(delayed) > F.col(visits))
    if clean.where(invalid).take(1):
        raise ValueError("Invalid identifier or count in the NHS source.")

    total = clean.where(F.col("organisation_code") == "TOTAL").select(
        "source_period", *COUNT_COLUMNS
    ).take(2)
    if len(total) != 1 or total[0]["source_period"] != "TOTAL":
        raise ValueError("Expected one England total row.")

    organisations = clean.where(F.col("organisation_code") != "TOTAL")
    if organisations.where(F.col("source_period") != SOURCE_PERIOD).take(1):
        raise ValueError("An organisation row has an unexpected reporting period.")

    totals = organisations.agg(
        F.count("*").alias("row_count"),
        F.countDistinct("organisation_code", "reporting_month").alias("key_count"),
        *(F.sum(name).alias(name) for name in COUNT_COLUMNS),
    ).first()
    if totals["row_count"] != 191 or totals["key_count"] != totals["row_count"]:
        raise ValueError("Expected 191 unique organisation-month keys.")
    mismatches = [name for name in COUNT_COLUMNS if totals[name] != total[0][name]]
    if mismatches:
        raise ValueError(f"Organisation counts differ from the England total: {mismatches}")
    return organisations


def to_gold(silver):
    return (
        silver.withColumn("type_1_attendances", F.col("unplanned_type_1") + F.col("booked_type_1"))
        .withColumn("type_1_over_4h", F.col("unplanned_over_4h_type_1") + F.col("booked_over_4h_type_1"))
        .withColumn("type_1_within_4h", F.col("type_1_attendances") - F.col("type_1_over_4h"))
        .select(
            "reporting_month", "organisation_code", "organisation_name", "parent_organisation",
            *METRIC_COLUMNS, "source_release_date", "source_sha256",
        )
    )


def england_summary(gold):
    result = gold.agg(
        F.count("*").alias("organisation_rows"),
        F.countDistinct("organisation_code", "reporting_month").alias("organisation_month_keys"),
        *(F.sum(name).alias(name) for name in METRIC_COLUMNS),
    )
    return result.withColumn(
        "type_1_within_4h_pct",
        F.round(100 * F.try_divide("type_1_within_4h", "type_1_attendances"), 1),
    )


def verify_gold(summary):
    row = summary.first()
    if (
        row["organisation_rows"] != 191
        or row["organisation_month_keys"] != 191
        or tuple(row[name] for name in METRIC_COLUMNS) != EXPECTED_TOTALS
        or row["type_1_within_4h_pct"] != 60.1
    ):
        raise ValueError(f"Gold does not match the October 2026 reference: {row.asDict()}")


def write_delta_slice(df, table, predicate):
    writer = df.write.format("delta").mode("overwrite").option("replaceWhere", predicate)
    writer.saveAsTable(table)


# COMMAND ----------

# MAGIC %md
# MAGIC Run the setup cell below, then upload the NHS CSV to the printed volume path.
# MAGIC Select **Run all** after the upload. The notebook processes the validated October 2026 release.

# COMMAND ----------

catalog = spark.sql("SELECT current_catalog()").first()[0]
if catalog in {"hive_metastore", "system", "samples"}:
    raise ValueError("Select the writable Unity Catalog catalog used for the environment check.")
catalog_sql = "`" + catalog.replace("`", "``") + "`"
project_schema = f"{catalog_sql}.nhs_ed"
volume_path = f"/Volumes/{catalog}/nhs_ed/raw"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {project_schema}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {project_schema}.raw")
print(f"Upload {SOURCE_FILE} to {volume_path}")

# COMMAND ----------

csv_path = f"{volume_path}/{SOURCE_FILE}"
try:
    bronze = read_release(spark, csv_path)
except FileNotFoundError as error:
    raise FileNotFoundError(f"Upload the NHS CSV to {csv_path} and run again.") from error

silver = to_silver(bronze)
gold = to_gold(silver)
verify_gold(england_summary(gold))

bronze_table = f"{project_schema}.bronze_ae_releases"
silver_table = f"{project_schema}.silver_ae_monthly"
gold_table = f"{project_schema}.fact_ae_monthly"
month_predicate = f"reporting_month = DATE '{REPORTING_MONTH}'"
release_predicate = f"{month_predicate} AND source_sha256 = '{SOURCE_SHA256}'"

write_delta_slice(bronze, bronze_table, release_predicate)
write_delta_slice(to_silver(spark.table(bronze_table).where(release_predicate)), silver_table, month_predicate)
write_delta_slice(to_gold(spark.table(silver_table).where(month_predicate)), gold_table, month_predicate)

summary = england_summary(spark.table(gold_table).where(month_predicate))
verify_gold(summary)
print(f"October 2026 checks passed. Import {gold_table} into Power BI.")
display(summary)
