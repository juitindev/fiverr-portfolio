"""
data_cleaner.py
================
Portfolio Example — "Clean, Process & Transform Your Messy Data"
By: jtccoder @ Fiverr

Scenario:
    A client provides a messy e-commerce orders CSV with:
    - Inconsistent date formats
    - Mixed currency symbols in price columns
    - Duplicate orders
    - Missing customer info
    - Inconsistent country names

Output:
    - cleaned_orders.csv     → clean, structured data
    - cleaning_report.txt    → summary of what was fixed
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import os

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE  = "messy_orders.csv"
OUTPUT_FILE = "cleaned_orders.csv"
REPORT_FILE = "cleaning_report.txt"

COUNTRY_MAP = {
    "usa": "United States", "u.s.a": "United States", "us": "United States",
    "uk": "United Kingdom", "u.k": "United Kingdom", "england": "United Kingdom",
    "taiwan": "Taiwan", "tw": "Taiwan", "台灣": "Taiwan",
    "japan": "Japan", "jp": "Japan", "jpn": "Japan",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def clean_price(value: str) -> float:
    """Remove currency symbols, commas, spaces → float."""
    if pd.isna(value):
        return np.nan
    cleaned = re.sub(r"[^\d.]", "", str(value))
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def parse_date(value: str) -> pd.Timestamp | None:
    """Try multiple date formats and return a unified Timestamp."""
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
        "%d-%m-%Y", "%Y/%m/%d", "%B %d, %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(str(value).strip(), fmt)
        except ValueError:
            continue
    return pd.NaT


def normalize_country(value: str) -> str:
    """Standardize country names using COUNTRY_MAP."""
    if pd.isna(value):
        return "Unknown"
    key = str(value).strip().lower().rstrip(".")
    return COUNTRY_MAP.get(key, str(value).strip().title())


def clean_phone(value: str) -> str:
    """Strip non-numeric chars, keep + prefix."""
    if pd.isna(value):
        return ""
    digits = re.sub(r"[^\d+]", "", str(value))
    return digits if digits else ""


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(input_file: str) -> tuple[pd.DataFrame, dict]:
    report = {}

    # 1. Load
    df = pd.read_csv(input_file, dtype=str, encoding="utf-8-sig")
    report["original_rows"] = len(df)
    report["original_cols"] = len(df.columns)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # 2. Drop rows where most fields are empty (threshold: >60% missing)
    threshold = int(len(df.columns) * 0.6)
    df.dropna(thresh=threshold, inplace=True)

    # 3. Remove duplicates (by order_id if exists, else full row)
    id_col = "order_id" if "order_id" in df.columns else None
    before = len(df)
    df.drop_duplicates(subset=[id_col] if id_col else None, keep="first", inplace=True)
    report["duplicates_removed"] = before - len(df)

    # 4. Clean price columns
    price_cols = [c for c in df.columns if "price" in c or "amount" in c or "total" in c]
    for col in price_cols:
        df[col] = df[col].apply(clean_price)
    report["price_cols_cleaned"] = price_cols

    # 5. Parse dates
    date_cols = [c for c in df.columns if "date" in c or "time" in c]
    for col in date_cols:
        df[col] = df[col].apply(parse_date)
        df[col] = pd.to_datetime(df[col], errors="coerce")
    report["date_cols_unified"] = date_cols

    # 6. Normalize country
    if "country" in df.columns:
        df["country"] = df["country"].apply(normalize_country)

    # 7. Clean phone
    if "phone" in df.columns:
        df["phone"] = df["phone"].apply(clean_phone)

    # 8. Standardize text columns (strip whitespace, title case for names)
    text_cols = [c for c in df.columns if df[c].dtype == object]
    for col in text_cols:
        df[col] = df[col].str.strip()

    name_cols = [c for c in df.columns if "name" in c]
    for col in name_cols:
        df[col] = df[col].str.title()

    # 9. Flag missing critical fields
    critical = [c for c in ["order_id", "customer_name", "email"] if c in df.columns]
    df["has_missing_critical"] = df[critical].isnull().any(axis=1)
    report["rows_with_missing_critical"] = int(df["has_missing_critical"].sum())

    # 10. Add metadata
    df["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report["final_rows"] = len(df)
    report["rows_cleaned"] = report["original_rows"] - report["duplicates_removed"]

    return df, report


def write_report(report: dict, path: str):
    lines = [
        "=" * 50,
        "  DATA CLEANING REPORT",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        f"Original rows       : {report['original_rows']}",
        f"Original columns    : {report['original_cols']}",
        f"Duplicates removed  : {report['duplicates_removed']}",
        f"Final rows          : {report['final_rows']}",
        f"Rows w/ missing data: {report['rows_with_missing_critical']}",
        "",
        f"Price cols cleaned  : {', '.join(report['price_cols_cleaned']) or 'None'}",
        f"Date cols unified   : {', '.join(report['date_cols_unified']) or 'None'}",
        "=" * 50,
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        # Generate a sample messy CSV for demo purposes
        sample = pd.DataFrame({
            "Order ID":        ["ORD001", "ORD002", "ORD002", "ORD003", None],
            "Customer Name":   ["john doe", "JANE SMITH", "JANE SMITH", "bob lee", None],
            "Email":           ["john@mail.com", "jane@mail.com", "jane@mail.com", None, None],
            "Phone":           ["+1-800-555-0101", "(02) 2345-6789", "(02) 2345-6789", "090-1234-5678", ""],
            "Order Date":      ["2024/01/15", "15/02/2024", "15/02/2024", "March 3, 2024", "bad-date"],
            "Total Amount":    ["$1,250.00", "NT$3,200", "NT$3,200", "¥45000", "???"],
            "Country":         ["usa", "Taiwan", "Taiwan", "jp", "england"],
        })
        sample.to_csv(INPUT_FILE, index=False)
        print(f"[Demo] Created sample file: {INPUT_FILE}")

    df_clean, report = run_pipeline(INPUT_FILE)
    df_clean.to_csv(OUTPUT_FILE, index=False)
    write_report(report, REPORT_FILE)
    print(f"\n✅ Done! Cleaned data → {OUTPUT_FILE}")
    print(f"📄 Report           → {REPORT_FILE}")
