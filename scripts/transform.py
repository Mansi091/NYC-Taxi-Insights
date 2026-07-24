import pandas as pd

print("Loading data...")
df = pd.read_parquet(r"../data/yellow_tripdata_2026-01.parquet")

print("Cleaning data...")
# 1. Drop missing values
df = df.dropna()

# 2. Drop duplicates & reset index to generate a unique trip_id
df = df.drop_duplicates().reset_index(drop=True)
df['trip_id'] = df.index

