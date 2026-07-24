import pandas as pd

print("Loading data...")
df = pd.read_parquet(r"../data/yellow_tripdata_2026-01.parquet")

print("Cleaning data...")
df = df.dropna()

df = df.drop_duplicates().reset_index(drop=True)
df['trip_id'] = df.index
