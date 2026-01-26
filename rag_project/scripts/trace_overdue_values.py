"""
Check if the merge/aggregation is causing the extreme overdue values
"""
import pandas as pd
import numpy as np

print("\n" + "="*80)
print("TRACING OVERDUE VALUES THROUGH AGGREGATION")
print("="*80)

# Load raw bureau
bureau = pd.read_csv('data/raw/bureau.csv')

# Focus on the problematic client 447111
test_client = 447111

print(f"\nClient {test_client} - Raw Bureau Records:")
print("="*80)
client_records = bureau[bureau['SK_ID_CURR'] == test_client]
print(f"Number of bureau records: {len(client_records)}")
print("\nAMT_CREDIT_MAX_OVERDUE values:")
print(client_records[['SK_ID_CURR', 'SK_ID_BUREAU', 'CREDIT_ACTIVE', 'AMT_CREDIT_MAX_OVERDUE', 'CREDIT_DAY_OVERDUE']])

print(f"\nAggregation check:")
print(f"  MAX(AMT_CREDIT_MAX_OVERDUE) = {client_records['AMT_CREDIT_MAX_OVERDUE'].max()}")
print(f"  SUM(AMT_CREDIT_MAX_OVERDUE) = {client_records['AMT_CREDIT_MAX_OVERDUE'].sum()}")
print(f"  MEAN(AMT_CREDIT_MAX_OVERDUE) = {client_records['AMT_CREDIT_MAX_OVERDUE'].mean():.2f}")

# Test another client with extreme values
print("\n" + "="*80)
print("Checking all clients with extreme overdue (>10 years):")
print("="*80)

# Find clients with any bureau record > 3650 days
extreme_records = bureau[bureau['AMT_CREDIT_MAX_OVERDUE'] > 3650]
print(f"\nBureau records with AMT_CREDIT_MAX_OVERDUE > 3650 days: {len(extreme_records)}")
print(f"Unique clients affected: {extreme_records['SK_ID_CURR'].nunique()}")

print("\nSample of extreme values (top 10):")
top_extreme = extreme_records.nlargest(10, 'AMT_CREDIT_MAX_OVERDUE')[['SK_ID_CURR', 'AMT_CREDIT_MAX_OVERDUE', 'CREDIT_ACTIVE', 'CREDIT_DAY_OVERDUE']]
print(top_extreme)

# Now simulate the aggregation
print("\n" + "="*80)
print("SIMULATING MERGE_AND_CLEAN AGGREGATION:")
print("="*80)

bureau_cols = [
    'SK_ID_CURR','CREDIT_ACTIVE','CREDIT_DAY_OVERDUE','AMT_CREDIT_SUM',
    'AMT_CREDIT_SUM_DEBT','AMT_CREDIT_SUM_OVERDUE','AMT_CREDIT_MAX_OVERDUE',
    'CNT_CREDIT_PROLONG','DAYS_CREDIT','DAYS_CREDIT_ENDDATE'
]
bureau = bureau[bureau_cols]

bureau['ACTIVE_NUM'] = bureau['CREDIT_ACTIVE'].apply(lambda x: 1 if x=='Active' else 0)

bureau_agg = bureau.groupby('SK_ID_CURR').agg({
    'ACTIVE_NUM':'sum',
    'AMT_CREDIT_SUM':'sum',
    'AMT_CREDIT_SUM_DEBT':'sum',
    'AMT_CREDIT_SUM_OVERDUE':'sum',
    'AMT_CREDIT_MAX_OVERDUE':'max',
    'CNT_CREDIT_PROLONG':'sum',
    'DAYS_CREDIT':'min',
    'DAYS_CREDIT_ENDDATE':'max',
    'CREDIT_DAY_OVERDUE':'max'
}).reset_index()

# Check client 447111 after aggregation
print(f"\nClient {test_client} after aggregation:")
agg_result = bureau_agg[bureau_agg['SK_ID_CURR'] == test_client]
print(agg_result[['SK_ID_CURR', 'AMT_CREDIT_MAX_OVERDUE', 'CREDIT_DAY_OVERDUE']])

# Check distribution of aggregated values
print("\n" + "="*80)
print("Distribution of max_overdue_days after aggregation:")
print("="*80)
print(f"Max value: {bureau_agg['AMT_CREDIT_MAX_OVERDUE'].max():,.0f}")
print(f"Values > 10 years (3650): {(bureau_agg['AMT_CREDIT_MAX_OVERDUE'] > 3650).sum()}")
print(f"Values > 5 years (1825): {(bureau_agg['AMT_CREDIT_MAX_OVERDUE'] > 1825).sum()}")
print(f"Values > 1 year (365): {(bureau_agg['AMT_CREDIT_MAX_OVERDUE'] > 365).sum()}")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("If AMT_CREDIT_MAX_OVERDUE values are the same before and after aggregation,")
print("then the extreme values are IN THE RAW DATA, not caused by the merge.")
