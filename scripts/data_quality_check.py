"""
data_quality_check.py
----------------------
Reusable data profiling, quality-check, and validation utility for the NYC
Taxi pipeline (or any tabular dataset with numeric/date columns).

Covers the core "data quality" workflow requested by data analyst roles:
    1. Data profiling        -> nulls, dtypes, cardinality per column
    2. Duplicate detection    -> exact-row duplicates
    3. Business-rule validation -> domain-specific sanity checks
       (negative fares, zero-distance trips, inconsistent totals, etc.)
    4. Before/after accuracy summary -> quantifies exactly what cleansing
       removed and why, for auditability

Can be run standalone (prints + writes a report) or imported and called from
the Mage AI transformer block / a notebook.

Usage:
    python scripts/data_quality_check.py data/sample_tripdata.parquet
"""
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Profiling
# ---------------------------------------------------------------------------
def profile_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Column-level profile: dtype, null count/%, unique count, sample value."""
    profile = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "null_count": df.isnull().sum(),
        "null_pct": (df.isnull().mean() * 100).round(2),
        "unique_count": df.nunique(),
    })
    profile["sample_value"] = [df[c].dropna().iloc[0] if df[c].notna().any() else None for c in df.columns]
    return profile


# ---------------------------------------------------------------------------
# 2. Duplicate detection
# ---------------------------------------------------------------------------
def find_duplicates(df: pd.DataFrame) -> dict:
    exact_dupes = df.duplicated().sum()
    return {
        "exact_duplicate_rows": int(exact_dupes),
        "exact_duplicate_pct": round(exact_dupes / len(df) * 100, 3) if len(df) else 0,
    }


# ---------------------------------------------------------------------------
# 3. Business-rule / anomaly validation
#    Each rule returns the row mask that VIOLATES the rule (i.e. "bad" rows)
# ---------------------------------------------------------------------------
def validate_business_rules(df: pd.DataFrame) -> dict:
    rules = {}

    if "fare_amount" in df.columns:
        rules["negative_fare_amount"] = df["fare_amount"] < 0

    if "trip_distance" in df.columns:
        rules["zero_or_negative_trip_distance"] = df["trip_distance"] <= 0

    if "passenger_count" in df.columns:
        rules["zero_passenger_count"] = df["passenger_count"] == 0
        rules["missing_passenger_count"] = df["passenger_count"].isna()

    if {"total_amount", "fare_amount"}.issubset(df.columns):
        rules["total_less_than_fare"] = df["total_amount"] < df["fare_amount"]

    if {"tpep_pickup_datetime", "tpep_dropoff_datetime"}.issubset(df.columns):
        rules["dropoff_before_pickup"] = df["tpep_dropoff_datetime"] < df["tpep_pickup_datetime"]

    summary = {}
    for rule_name, mask in rules.items():
        mask = mask.fillna(False)
        summary[rule_name] = {
            "violation_count": int(mask.sum()),
            "violation_pct": round(mask.sum() / len(df) * 100, 3) if len(df) else 0,
        }
    return summary, rules


# ---------------------------------------------------------------------------
# 4. Cleansing pass + before/after accuracy summary
# ---------------------------------------------------------------------------
def clean_dataset(df: pd.DataFrame):
    """Applies the same cleansing logic as the pipeline's transformer block,
    but tracks exactly what was removed and why, for auditability."""
    before_rows = len(df)
    log = {"starting_rows": before_rows}

    # duplicates
    df1 = df.drop_duplicates()
    log["duplicates_removed"] = before_rows - len(df1)

    # nulls in required columns
    required_cols = [c for c in ["fare_amount", "trip_distance", "tpep_pickup_datetime"] if c in df.columns]
    df2 = df1.dropna(subset=required_cols) if required_cols else df1.dropna()
    log["null_rows_removed"] = len(df1) - len(df2)

    # business-rule violations
    _, rule_masks = validate_business_rules(df2)
    combined_bad_mask = pd.Series(False, index=df2.index)
    for mask in rule_masks.values():
        combined_bad_mask = combined_bad_mask | mask.reindex(df2.index).fillna(False)

    df3 = df2[~combined_bad_mask].reset_index(drop=True)
    log["anomaly_rows_removed"] = int(combined_bad_mask.sum())

    log["final_rows"] = len(df3)
    log["total_rows_removed"] = before_rows - len(df3)
    log["pct_rows_removed"] = round(log["total_rows_removed"] / before_rows * 100, 2) if before_rows else 0
    log["pct_rows_retained"] = round(100 - log["pct_rows_removed"], 2)

    return df3, log


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_full_report(path: str, out_dir: str = "data"):
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)

    profile = profile_dataset(df)
    dupes = find_duplicates(df)
    rule_summary, _ = validate_business_rules(df)
    cleaned_df, clean_log = clean_dataset(df)

    print("=" * 70)
    print("DATA QUALITY REPORT")
    print("=" * 70)
    print(f"\nSource: {path}")
    print(f"Rows x Columns: {df.shape[0]} x {df.shape[1]}\n")

    print("--- Column Profile (nulls, dtype, cardinality) ---")
    print(profile.to_string())

    print("\n--- Duplicate Check ---")
    print(json.dumps(dupes, indent=2))

    print("\n--- Business Rule Violations ---")
    print(json.dumps(rule_summary, indent=2))

    print("\n--- Cleansing Summary (before -> after) ---")
    print(json.dumps(clean_log, indent=2))
    print(f"\n{clean_log['pct_rows_retained']}% of rows passed all quality checks "
          f"and were retained; {clean_log['pct_rows_removed']}% were dropped "
          f"(duplicates, nulls in required fields, or rule violations).")

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    profile.to_csv(f"{out_dir}/dq_column_profile.csv")
    with open(f"{out_dir}/dq_report.json", "w") as f:
        json.dump({
            "source": path,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "duplicates": dupes,
            "business_rule_violations": rule_summary,
            "cleansing_summary": clean_log,
        }, f, indent=2, default=str)
    cleaned_df.to_parquet(f"{out_dir}/cleaned_tripdata.parquet", index=False)

    print(f"\nSaved: {out_dir}/dq_column_profile.csv, {out_dir}/dq_report.json, "
          f"{out_dir}/cleaned_tripdata.parquet")

    return df, cleaned_df, clean_log


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/sample_tripdata.parquet"
    run_full_report(src)
