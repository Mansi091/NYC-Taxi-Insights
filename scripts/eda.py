import pandas as pd

print("Loading data for EDA...")
df = pd.read_parquet(r"../data/yellow_tripdata_2026-01.parquet")


print("EXPLORATORY DATA ANALYSIS")


print("data shape")
print(df.shape)

print("\n data types and null counts")
print(df.info())

print("\n missing values")
print(df.isnull().sum())

print("\n summary statistics")
print(df.describe())

print("\n duplicate values " )
print(f"Total duplicate rows: {df.duplicated().sum()}")

print("Dropping missing rows while the count of missing rows is very large")

df = df.dropna()
print(df.isnull().sum())

print("final size")
print(df.size)


print("final cleaned first 5 rows")
pd.set_option('display.max_columns', None)
print(df.head())

print("All columns present :")
print(df.columns)

print("\n--- 6. PAYMENT TYPES ---")
print(df['payment_type'].value_counts())

