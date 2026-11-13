"""Reproduce the NHS source checks using a small sample of public CSV files."""

import csv
import hashlib
import html
import io
import json
import re
from calendar import month_name
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from urllib.request import Request, urlopen

NHS = "https://www.england.nhs.uk/statistics/"
UPLOADS = NHS + "wp-content/uploads/sites/2/"
YEARS = ("2023-24", "2024-25", "2025-26", "2026-27")
SAMPLES = {
    ("2023-06", "original"): "2023/07/Monthly-AE-June-2023.csv",
    ("2023-06", "revised"): "2024/06/June-2023-revised-130624-ndcvf47.csv",
    ("2024-07", "original"): "2024/08/Monthly-AE-July-2024.csv",
    ("2024-07", "revised"): "2024/11/Monthly-AE-July-2024-revised.csv",
    ("2026-03", "revised"): "2026/05/Monthly-AE-March-2026-revised-flkg42.csv",
    ("2026-04", "revised"): "2026/11/April-2026-Revised-12.11.26-CSV-28KB-aW27FD.csv",
    ("2026-10", "original"): "2026/11/October-2026-CSV-WD35qg.csv",
}
IDS = ("Period", "Org Code", "Parent Org", "Org name")
COUNTS = (
    "A&E attendances Type 1",
    "A&E attendances Type 2",
    "A&E attendances Other A&E Department",
    "A&E attendances Booked Appointments Type 1",
    "A&E attendances Booked Appointments Type 2",
    "A&E attendances Booked Appointments Other Department",
    "Attendances over 4hrs Type 1",
    "Attendances over 4hrs Type 2",
    "Attendances over 4hrs Other Department",
    "Attendances over 4hrs Booked Appointments Type 1",
    "Attendances over 4hrs Booked Appointments Type 2",
    "Attendances over 4hrs Booked Appointments Other Department",
    "Patients who have waited 4-12 hs from DTA to admission",
    "Patients who have waited 12+ hrs from DTA to admission",
    "Emergency admissions via A&E - Type 1",
    "Emergency admissions via A&E - Type 2",
    "Emergency admissions via A&E - Other A&E department",
    "Other emergency admissions",
)


def fetch(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        return response.read()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def index_months(fiscal_year):
    url = (NHS + "wp-json/wp/v2/pages?slug=ae-attendances-and-emergency-admissions-"
           + fiscal_year + "&_fields=link,content")
    page, = json.loads(fetch(url))
    links = re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page["content"]["rendered"], re.S)
    months = {}
    for href, label in links:
        href = html.unescape(href)
        label = html.unescape(re.sub(r"<[^>]+>", " ", label))
        match = re.search(r"Monthly A&E\s+([A-Za-z]+)\s+(\d{4})", label)
        if href.lower().endswith(".csv") and match:
            month, year = match.groups()
            key = f"{year}-{list(month_name).index(month):02}"
            require(key not in months, f"Multiple current index links for {key}")
            months[key] = {"url": href, "label": label.strip()}
    return {"url": url, "months": months}


def validate_file(sample):
    (month, version), path = sample
    url = UPLOADS + path
    raw = fetch(url)
    csv_rows = csv.reader(io.StringIO(raw.decode("utf-8-sig")), strict=True)
    header = tuple(next(csv_rows))
    require(header == IDS + COUNTS, f"Unexpected CSV schema: {url}")
    year, month_number = month.split("-")
    expected_period = f"MSITAE-{month_name[int(month_number)].upper()}-{year}"
    providers = {}
    total = None
    total_label = None
    for line, row in enumerate(csv_rows, 2):
        require(len(row) == len(header), f"Wrong column count at {url}:{line}")
        period, code, parent, name = (value.strip() for value in row[:4])
        require(all((period, code, parent, name)), f"Blank identifier at {url}:{line}")
        fields = [value.strip() for value in row[4:]]
        require(all(re.fullmatch(r"[0-9]+", field) for field in fields), f"Invalid count at {url}:{line}")
        counts = tuple(map(int, fields))
        require(all(late <= n for n, late in zip(counts[:6], counts[6:12])),
                f"Over-four-hour counts exceed attendances at {url}:{line}")
        if code.upper() == "TOTAL":
            require(total is None and period.upper() == "TOTAL", f"Unexpected total row at {url}:{line}")
            total = counts
            total_label = code
            continue
        code = code.upper()
        require(period.upper() == expected_period, f"Wrong reporting month at {url}:{line}")
        require(code not in providers, f"Duplicate organisation {code} at {url}:{line}")
        providers[code] = counts
    require(providers and total is not None, f"No provider rows or missing total: {url}")
    require(tuple(map(sum, zip(*providers.values()))) == total, f"Provider counts differ from TOTAL: {url}")
    return (month, version), {
        "url": url,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "organisation_rows": len(providers),
        "total_row_label": total_label,
        "england_totals": dict(zip(COUNTS, total)),
    }, providers


def compare_releases(original, revised):
    original_record, original_providers = original
    revised_record, revised_providers = revised
    shared_codes = original_providers.keys() & revised_providers.keys()
    changes = {}
    for column in COUNTS:
        difference = revised_record["england_totals"][column] - original_record["england_totals"][column]
        if difference:
            changes[column] = difference
    return {
        "added_organisations": sorted(revised_providers.keys() - original_providers.keys()),
        "removed_organisations": sorted(original_providers.keys() - revised_providers.keys()),
        "organisations_with_changed_counts": sorted(
            code for code in shared_codes if original_providers[code] != revised_providers[code]
        ),
        "england_total_change": changes,
    }


def october_reference(totals):
    attendances = totals[COUNTS[0]] + totals[COUNTS[3]]
    over_four_hours = totals[COUNTS[6]] + totals[COUNTS[9]]
    within_four_hours = attendances - over_four_hours
    rate = (Decimal(within_four_hours) * 100 / attendances).quantize(Decimal("0.1"))
    result = {
        "type_1_attendances": attendances,
        "type_1_over_four_hours": over_four_hours,
        "type_1_within_four_hours": within_four_hours,
        "type_1_within_four_hours_pct": str(rate),
        "type_1_emergency_admissions": totals[COUNTS[14]],
        "all_ae_types_dta_over_twelve_hours": totals[COUNTS[13]],
    }
    # Reference values are from the October 2026 Statistical Commentary, page 2.
    require(within_four_hours == 931_279 and rate == Decimal("60.1") and totals[COUNTS[13]] == 57_840,
            "October 2026 results differ from NHS statistical commentary")
    return result


def main():
    with ThreadPoolExecutor(max_workers=4) as executor:
        indices = dict(zip(YEARS, executor.map(index_months, YEARS)))
        records = {key: (profile, rows) for key, profile, rows in executor.map(validate_file, SAMPLES.items())}
    listed = {}
    for index in indices.values():
        for key, link in index["months"].items():
            require(key not in listed, f"Multiple fiscal-year indices list {key}")
            listed[key] = link
    expected = [f"{year}-{month:02}" for year in range(2023, 2027) for month in range(1, 13)
                if "2023-06" <= f"{year}-{month:02}" <= "2026-10"]
    require(set(expected) <= listed.keys(), "Missing monthly CSV links in the expected window")
    for key, (record, _) in records.items():
        month, _ = key
        if (month, "revised") not in records or key[1] == "revised":
            require(listed[month]["url"] == record["url"], f"NHS now lists a different release for {month}")
    result = {
        "indexed_window": [expected[0], expected[-1]],
        "months_with_csv_links": len(expected),
        "index_urls": [index["url"] for index in indices.values()],
        "csv_columns": len(IDS + COUNTS),
        "samples": {"/".join(key): record for key, (record, _) in records.items()},
        "revision_comparisons": {
            month: compare_releases(records[month, "original"], records[month, "revised"])
            for month in ("2023-06", "2024-07")
        },
        "october_2026_reference": october_reference(records["2026-10", "original"][0]["england_totals"]),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
