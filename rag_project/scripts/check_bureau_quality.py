"""
Check bureau.csv for data quality issues in AMT_CREDIT_MAX_OVERDUE
"""
import pandas as pd
import numpy as np

print("\n" + "="*80)
print("CHECKING BUREAU.CSV FOR OVERDUE DATA QUALITY")
print("="*80)

bureau = pd.read_csv('data/raw/bureau.csv')

print(f"\nTotal bureau records: {len(bureau):,}")

# Check AMT_CREDIT_MAX_OVERDUE
print("\n" + "-"*80)
print("AMT_CREDIT_MAX_OVERDUE Statistics:")
print("-"*80)
print(bureau['AMT_CREDIT_MAX_OVERDUE'].describe())

print("\n" + "-"*80)
print("Distribution Analysis:")
print("-"*80)
print(f"Non-zero values: {(bureau['AMT_CREDIT_MAX_OVERDUE'] > 0).sum():,}")
print(f"Values > 1 year (365 days): {(bureau['AMT_CREDIT_MAX_OVERDUE'] > 365).sum():,}")
print(f"Values > 5 years (1825 days): {(bureau['AMT_CREDIT_MAX_OVERDUE'] > 1825).sum():,}")
print(f"Values > 10 years (3650 days): {(bureau['AMT_CREDIT_MAX_OVERDUE'] > 3650).sum():,}")
print(f"Values > 50 years (18250 days): {(bureau['AMT_CREDIT_MAX_OVERDUE'] > 18250).sum():,}")

print("\n" + "-"*80)
print("Top 20 Highest Values:")
print("-"*80)
top_values = bureau['AMT_CREDIT_MAX_OVERDUE'].nlargest(20)
for i, val in enumerate(top_values.values, 1):
    years = val / 365
    print(f"{i:2d}. {val:>10,.0f} days = {years:>6.1f} years")

# Check clients with extreme values
print("\n" + "-"*80)
print("Sample Clients with Extreme Overdue (>10 years):")
print("-"*80)
extreme = bureau[bureau['AMT_CREDIT_MAX_OVERDUE'] > 3650][['SK_ID_CURR', 'AMT_CREDIT_MAX_OVERDUE', 'CREDIT_ACTIVE', 'CREDIT_DAY_OVERDUE']].head(10)
print(extreme)

# Check if these are nulls encoded as large numbers
print("\n" + "-"*80)
print("Checking for patterns:")
print("-"*80)
print(f"Max value: {bureau['AMT_CREDIT_MAX_OVERDUE'].max():,.0f}")
print(f"99th percentile: {bureau['AMT_CREDIT_MAX_OVERDUE'].quantile(0.99):,.0f}")
print(f"95th percentile: {bureau['AMT_CREDIT_MAX_OVERDUE'].quantile(0.95):,.0f}")
print(f"90th percentile: {bureau['AMT_CREDIT_MAX_OVERDUE'].quantile(0.90):,.0f}")
