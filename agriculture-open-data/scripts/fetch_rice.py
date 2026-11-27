#!/usr/bin/env python3
"""Fetch MOA TownRiceData and write an Excel-readable UTF-8 CSV."""

import argparse
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

ENDPOINT = "https://data.moa.gov.tw/Service/OpenData/FromM/TownRiceData.aspx"
FIELDS = (
    "年度", "期作", "縣市", "鄉鎮", "作物代碼", "作物", "種植面積", "收穫面積",
    "稻穀總產量", "稻穀單位產量", "糙米總產量", "糙米單位產量",
)
PAGE_SIZE = 1000


def roc_year(value):
    if value.isascii() and value.isdecimal():
        year = int(value)
        if len(value) == 4 and year >= 1912:
            return str(year - 1911)
        if len(value) <= 3 and year > 0:
            return str(year)
    raise argparse.ArgumentTypeError("請輸入民國年（如 113）或西元年（如 2024）")


def fetch_page(params):
    with urlopen(f"{ENDPOINT}?{urlencode(params)}", timeout=30) as response:
        rows = json.loads(response.read().decode("utf-8-sig"))
    if not isinstance(rows, list) or any(
        not isinstance(row, dict) or not set(FIELDS).issubset(row)
        for row in rows
    ):
        raise ValueError("API 回傳格式或欄位與 EIR837 規格不符")
    return rows


def fetch_rows(filters):
    rows = []
    seen_pages = set()
    while True:
        page = fetch_page({**filters, "$top": PAGE_SIZE, "$skip": len(rows)})
        if not page:
            return rows
        signature = json.dumps(page, sort_keys=True, ensure_ascii=False)
        if signature in seen_pages:
            raise ValueError(f"API 回傳重複頁面（略過 {len(rows)} 筆），無法確認完整性")
        seen_pages.add(signature)
        rows.extend(page)


def write_csv(destination, rows):
    fields = list(FIELDS)
    fields.extend(sorted({key for row in rows for key in row}.difference(FIELDS)))
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8-sig", newline="", dir=destination.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        # Publish only after all queries and the CSV write succeed.
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=roc_year, action="append", help="民國或西元年，可重複")
    parser.add_argument("--period")
    parser.add_argument("--city")
    parser.add_argument("--town")
    crop = parser.add_mutually_exclusive_group()
    crop.add_argument("--crop-code", type=str.upper)
    crop.add_argument("--crop")
    parser.add_argument("--output", type=Path, required=True, help="新建 CSV 的路徑")
    args = parser.parse_args()
    filters = {
        key: value for key, value in {
            "name": args.period, "city": args.city, "town": args.town,
            "cropCode": args.crop_code, "crop": args.crop,
        }.items() if value is not None
    }
    rows = []
    batches = []
    try:
        for year in dict.fromkeys(args.year or [None]):
            query = {**filters, "year": year} if year else filters
            try:
                batch = fetch_rows(query)
            except (URLError, OSError, ValueError) as error:
                raise ValueError(f"查詢 {query!r} 失敗：{error}") from error
            batches.append({"filters": query, "rows": len(batch)})
            rows.extend(batch)
        write_csv(args.output, rows)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps({
        "source": ENDPOINT, "retrieved_at": datetime.now().astimezone().isoformat(),
        "output": str(args.output.resolve()), "batches": batches, "rows": len(rows),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
