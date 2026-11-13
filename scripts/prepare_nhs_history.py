"""Download and validate the fixed June 2023–October 2026 history bundle."""

import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

from validate_nhs_inputs import SAMPLES, UPLOADS, YEARS, fetch, index_months

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "notebooks"))
from history_pipeline import BUNDLE_NAME, HISTORY_MONTHS, require, stage_bundle, validate_release

# Published date checked against the October 2026 statistical release.
OCTOBER_RELEASE = "2026-11-12"


def release_date(month, label):
    revision = re.search(r"revised\s+(\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2}))\b", label, re.I)
    if revision:
        value = revision[1]
        pattern = "%d.%m.%Y" if len(value.rsplit(".", 1)[1]) == 4 else "%d.%m.%y"
        return datetime.strptime(value, pattern).date().isoformat()
    return OCTOBER_RELEASE if month == "2026-10-01" and "revised" not in label.lower() else None


def download_release(item):
    month, url, label, is_current = item
    path = urlsplit(url)
    require(url.startswith(UPLOADS) and path.path.lower().endswith(".csv"), f"Unexpected source URL: {url}")
    entry = {
        "reporting_month": month,
        "source_url": url,
        "source_release_date": release_date(month, label) if is_current else None,
        "filename": path.path.rsplit("/", 1)[-1],
        "label": label,
        "is_current": is_current,
    }
    raw = fetch(url)
    entry["source_sha256"] = hashlib.sha256(raw).hexdigest()
    validate_release(entry, raw)
    return entry, raw


def main():
    with ThreadPoolExecutor(max_workers=8) as pool:
        indices = list(pool.map(index_months, YEARS))
        items = [
            (f"{month}-01", link["url"], link["label"], True)
            for index in indices
            for month, link in index["months"].items()
            if f"{month}-01" in HISTORY_MONTHS
        ]
        items.extend(
            (f"{month}-01", UPLOADS + path, "Original publication", False)
            for (month, version), path in SAMPLES.items()
            if version == "original" and month in {"2023-06", "2024-07"}
        )
        downloads = list(pool.map(download_release, sorted(items)))

    output = PROJECT / "data" / BUNDLE_NAME
    output.parent.mkdir(exist_ok=True)
    manifest = {
        "format_version": 1,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "index_urls": [index["url"] for index in indices],
        "releases": [entry for entry, _ in downloads],
    }
    with TemporaryDirectory(dir=output.parent) as temporary:
        candidate = Path(temporary) / output.name
        with ZipFile(candidate, "w", compression=ZIP_DEFLATED) as bundle:
            for entry, raw in downloads:
                bundle.writestr(entry["filename"], raw)
            bundle.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        expected, release_counts, revisions = stage_bundle(candidate, Path(temporary) / "records.json")
        candidate.replace(output)

    print(f"{len(expected)} months, {sum(item[1] for item in expected.values()):,} organisation-month rows, "
          f"{len(release_counts)} releases and {sum(release_counts.values()):,} Bronze rows.")
    for month, versions in sorted(revisions.items()):
        _, original = versions[False]
        _, current = versions[True]
        print(f"{month}: {len(original)} to {len(current)} organisations. "
              f"Added: {', '.join(sorted(current - original)) or 'none'}. "
              f"Removed: {', '.join(sorted(original - current)) or 'none'}.")
    print(f"Created {output} ({output.stat().st_size:,} bytes).")


if __name__ == "__main__":
    main()
