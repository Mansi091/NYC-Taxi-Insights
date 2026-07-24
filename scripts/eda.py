import pandas as pd

print("Loading data for EDA...")
df = pd.read_parquet(r"../data/yellow_tripdata_2026-01.parquet")

print("\n==============================")
print("     EXPLORATORY DATA ANALYSIS")
print("==============================\n")

print("--- 1. DATA SHAPE (Rows, Columns) ---")
print(df.shape)

print("\n--- 2. DATA TYPES & NON-NULL COUNTS ---")
print(df.info())

print("\n--- 3. MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- 4. SUMMARY STATISTICS (Numerical Columns) ---")
print(df.describe())

print("\n--- 5. CHECKING FOR DUPLICATES ---")
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

