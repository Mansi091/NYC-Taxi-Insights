"""
make_sample_data.py
--------------------
Generates a small SYNTHETIC sample of yellow-taxi-style trip records for local
testing/demo of the data quality and reporting scripts, since the real NYC TLC
parquet file (~1GB+) isn't checked into the repo.

This is NOT real trip data — it mimics the schema and injects realistic data
quality issues (nulls, duplicates, negative fares, zero-distance trips) so the
data_quality_check.py script has something meaningful to catch.

Usage:
    python scripts/make_sample_data.py
Output:
    data/sample_tripdata.parquet
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 5000

pickup = pd.to_datetime("2026-01-01") + pd.to_timedelta(
    rng.integers(0, 31 * 24 * 60, N), unit="m"
)
trip_minutes = rng.integers(2, 60, N)
dropoff = pickup + pd.to_timedelta(trip_minutes, unit="m")

trip_distance = np.round(rng.exponential(2.5, N), 2)
fare_amount = np.round(trip_distance * rng.uniform(2.5, 4.0, N) + 2.5, 2)
tip_amount = np.round(fare_amount * rng.uniform(0, 0.25, N), 2)
tolls_amount = np.round(rng.choice([0, 0, 0, 6.55], N), 2)
total_amount = np.round(fare_amount + tip_amount + tolls_amount, 2)

df = pd.DataFrame({
    "VendorID": rng.choice([1, 2], N),
    "tpep_pickup_datetime": pickup,
    "tpep_dropoff_datetime": dropoff,
    "passenger_count": rng.choice([1, 1, 1, 2, 3, 4, 0], N).astype(float),
    "trip_distance": trip_distance,
    "RatecodeID": rng.choice([1, 1, 1, 2, 3, 4, 5, 6], N).astype(float),
    "PULocationID": rng.integers(1, 265, N),
    "DOLocationID": rng.integers(1, 265, N),
    "payment_type": rng.choice([1, 1, 2, 2, 3, 4], N),
    "fare_amount": fare_amount,
    "tip_amount": tip_amount,
    "tolls_amount": tolls_amount,
    "total_amount": total_amount,
})

# --- inject realistic data quality issues on purpose ---
null_idx = rng.choice(df.index, size=int(N * 0.03), replace=False)
df.loc[null_idx, "passenger_count"] = np.nan

null_idx2 = rng.choice(df.index, size=int(N * 0.01), replace=False)
df.loc[null_idx2, "RatecodeID"] = np.nan

# duplicate ~1% of rows
dupe_rows = df.sample(frac=0.01, random_state=1)
df = pd.concat([df, dupe_rows], ignore_index=True)

# a few negative / zero-value anomalies that shouldn't exist in clean data
bad_idx = rng.choice(df.index, size=15, replace=False)
df.loc[bad_idx[:5], "fare_amount"] = -df.loc[bad_idx[:5], "fare_amount"]
df.loc[bad_idx[5:10], "trip_distance"] = 0
df.loc[bad_idx[10:], "total_amount"] = df.loc[bad_idx[10:], "fare_amount"] - 50  # total < fare, inconsistent

df.to_parquet("data/sample_tripdata.parquet", index=False)
print(f"Wrote data/sample_tripdata.parquet with {len(df)} rows (synthetic, includes injected DQ issues)")
