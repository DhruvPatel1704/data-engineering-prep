# Day 08 — Python + Pandas Basics
# Focus: Series, DataFrame, indexing, dtypes, exploration
# Dataset: Uber rides (loaded directly from URL)

import pandas as pd

# 1. Load dataset
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv"
)

# 2. Basic inspection
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

# 3. Data types
print("\nData types:")
print(df.dtypes)

# 4. First look at data
print("\nFirst 5 rows:")
print(df.head())

# 5. Null check — important before any transformation
print("\nNull counts per column:")
print(df.isnull().sum())

# 6. Summary statistics
print("\nDescriptive stats:")
print(df.describe())

# 7. Series basics — mean, std, sum
s = pd.Series([10, 20, 30, 40, 50], name="sample")
print("\nSeries mean:", s.mean())
print("Series std:", round(s.std(), 2))
print("Series sum:", s.sum())

# 8. Boolean indexing on Series
print("\nValues above 25:")
print(s[s > 25])

# 9. Value counts on first column
print("\nValue counts (top 10):")
print(df.iloc[:, 0].value_counts().head(10))

# 10. loc vs iloc difference
# loc = label based, iloc = position based
print("\nloc rows 0 to 2:")
print(df.loc[0:2])

print("\niloc first 2 rows, first 3 columns:")
print(df.iloc[0:2, 0:3])

# 11. Normalize column names — standard practice before any pipeline work
df.columns = [c.lower().replace(" ", "_") for c in df.columns]
print("\nNormalized column names:", df.columns.tolist())

# 12. Add a calculated column
df["row_index"] = range(len(df))
print("\nAdded row_index. Shape:", df.shape)

# 13. Drop column
df = df.drop(columns=["row_index"])
print("Dropped row_index. Shape:", df.shape)

# 14. Sort by first column descending
df_sorted = df.sort_values(by=df.columns[0], ascending=False)
print("\nSorted by", df.columns[0], "descending:")
print(df_sorted.head(3))

# 15. Basic groupby count
print("\nGroupby count on first column:")
print(df.groupby(df.columns[0]).size().head(5))

# 16. Apply lambda to last column
df["col_doubled"] = df.iloc[:, -1].apply(lambda x: x * 2 if pd.notnull(x) else x)
print("\nDoubled last column sample:")
print(df["col_doubled"].head(5))

# 17. Drop duplicates
before = len(df)
df = df.drop_duplicates()
after = len(df)
print(f"\nDuplicate rows removed: {before - after}")

# 18. Save cleaned output
df.to_csv("day08_output.csv", index=False)
print("\nSaved to day08_output.csv")
print("Day 08 complete")
