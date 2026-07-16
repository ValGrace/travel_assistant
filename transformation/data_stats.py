import pandas as pd
import numpy as np

entities_frame = pd.read_json(
   "data/raw_data/kenyan_hotels.json"
)

print(f"\n{'='*60}")
print(f"DATASET OVERVIEW")
print(f"{'='*60}")
print(f"Rows:       {entities_frame.shape[0]:,}")
print(f"Columns:    {entities_frame.shape[1]}")

print(f"\n{'='*60}")
print("SCHEMA SUMMARY")
print(f"{'='*60}")
print(f"{'#':<4}  {'Column':<40} {'dtype':<15} {'Empty Values':<12} {'Null Count':<12} {'Null %':<12} {'Sample Values'}")
print(f"{'-'*4} {'-'*40} {'-'*15} {'-'*12} {'-'*12} {'-'*8} {'-'*30}")

for i, col in enumerate(entities_frame.columns):
    dtype = str(entities_frame[col].dtype)
    non_null = (entities_frame[col].values == "").sum()
    null_count = (entities_frame[col].values == "NULL").sum()
    null_pct = null_count / len(entities_frame) * 100
    # sample unique non-null values (up to 3)
    samples = entities_frame[col].dropna()
    sample_str = ",  ".join([str(s) for s in samples])[:50]
    print(f"{i:<5}  {col:<40}  {dtype:<15}  {non_null:<12,}  {null_count:<12,} {null_pct:<8.2f} {sample_str}")

# __________ sample rows ____________________________________________
print(f"\n{'='*60}")
print("SAMPLE ROWS (first 5)")
print(f"{'='*60}")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', 60)
print(entities_frame.head(15))



categories = entities_frame.select_dtypes(include=['object', 'category']).columns.tolist()
print(f"\n{'='*60}")
print(f"CATEGORICAL / OBJECT COLUMNS  ({len(categories)})")
print(f"{'='*60}")
pd.set_option('display.max_columns', None)
for col in categories:
    series = entities_frame[col]

    # If dicts are present, convert to string
    if series.apply(lambda x: isinstance(x, dict)).any():
        series = series.astype(str)

    n_unique = series.nunique()
    top_values = series.value_counts().head(5).to_dict()

    print(f"\n  {col}  [unique: {n_unique}]")
    for val, cnt in top_values.items():
        pct = cnt / len(series) * 100
        print(f"    {str(val):<35}  {cnt:>8,}    ({pct:.2f}%)")

