import pandas as pd
import numpy as np

# ---------------------------
# 1️⃣ Load raw CSVs
# ---------------------------
application = pd.read_csv("data/raw/application_train.csv")
previous = pd.read_csv("data/raw/previous_application.csv")
bureau = pd.read_csv("data/raw/bureau.csv")
installments = pd.read_csv("data/raw/installments_payments.csv")

# ---------------------------
# 2️⃣ Aggregate previous_application per SK_ID_CURR
# ---------------------------
# Only keep MVP columns
prev_cols = [
    'SK_ID_CURR', 'NAME_CONTRACT_STATUS', 'AMT_APPLICATION', 'AMT_CREDIT', 
    'AMT_ANNUITY', 'NAME_CONTRACT_TYPE', 'NAME_CASH_LOAN_PURPOSE', 
    'NAME_PORTFOLIO', 'NAME_CLIENT_TYPE', 'CNT_PAYMENT', 'NAME_YIELD_GROUP'
]
previous = previous[prev_cols]

# Encode contract status as numerical
previous['STATUS_ACCEPTED'] = previous['NAME_CONTRACT_STATUS'].apply(lambda x: 1 if x=='Approved' else 0)
previous['STATUS_REFUSED'] = previous['NAME_CONTRACT_STATUS'].apply(lambda x: 1 if x=='Refused' else 0)

# Aggregation
previous_agg = previous.groupby('SK_ID_CURR').agg({
    'STATUS_ACCEPTED':'mean',            # % accepted
    'STATUS_REFUSED':'mean',             # % refused
    'AMT_CREDIT':'mean',
    'AMT_ANNUITY':'mean',
    'AMT_APPLICATION':'mean',
    'CNT_PAYMENT':'mean',
    'NAME_CLIENT_TYPE': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown',
    'NAME_YIELD_GROUP': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
}).reset_index()

# ---------------------------
# 3️⃣ Aggregate bureau per SK_ID_CURR
# ---------------------------
bureau_cols = [
    'SK_ID_CURR','CREDIT_ACTIVE','CREDIT_DAY_OVERDUE','AMT_CREDIT_SUM',
    'AMT_CREDIT_SUM_DEBT','AMT_CREDIT_SUM_OVERDUE','AMT_CREDIT_MAX_OVERDUE',
    'CNT_CREDIT_PROLONG','DAYS_CREDIT','DAYS_CREDIT_ENDDATE'
]
bureau = bureau[bureau_cols]

# Convert CREDIT_ACTIVE to numeric
bureau['ACTIVE_NUM'] = bureau['CREDIT_ACTIVE'].apply(lambda x: 1 if x=='Active' else 0)

# Aggregation
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
}).reset_index().rename(columns={
    'ACTIVE_NUM':'nb_active_credits',
    'AMT_CREDIT_SUM':'total_external_credit',
    'AMT_CREDIT_SUM_DEBT':'total_external_debt',
    'AMT_CREDIT_SUM_OVERDUE':'sum_overdue_amount',
    'AMT_CREDIT_MAX_OVERDUE':'max_overdue_days',
    'CNT_CREDIT_PROLONG':'total_prolongations',
    'DAYS_CREDIT':'first_credit_days',
    'DAYS_CREDIT_ENDDATE':'last_credit_days',
    'CREDIT_DAY_OVERDUE':'current_overdue_days'
})

# ---------------------------
# 4️⃣ Aggregate installments_payments per SK_ID_CURR
# ---------------------------
inst_cols = ['SK_ID_CURR','AMT_INSTALMENT','AMT_PAYMENT','DAYS_ENTRY_PAYMENT','DAYS_INSTALMENT']
installments = installments[inst_cols]

# Compute delays
installments['delay'] = installments['DAYS_ENTRY_PAYMENT'] - installments['DAYS_INSTALMENT']

# Aggregation per client
installments_agg = installments.groupby('SK_ID_CURR').agg({
    'delay':'mean',
    'AMT_PAYMENT':'sum',
    'AMT_INSTALMENT':'sum'
}).reset_index().rename(columns={
    'delay':'avg_payment_delay',
    'AMT_PAYMENT':'total_paid',
    'AMT_INSTALMENT':'total_due'
})
# Avoid division by zero
installments_agg['payment_ratio'] = installments_agg.apply(
    lambda x: x['total_paid'] / x['total_due'] if x['total_due'] > 0 else 0, axis=1
)

# ---------------------------
# 5️⃣ Merge all with application_train
# ---------------------------
df = application.copy()

# Merge aggregated tables (add suffixes to avoid conflicts)
df = df.merge(previous_agg, on='SK_ID_CURR', how='left', suffixes=('', '_prev'))
df = df.merge(bureau_agg, on='SK_ID_CURR', how='left')
df = df.merge(installments_agg, on='SK_ID_CURR', how='left')

# ---------------------------
# 6️⃣ Add temporal metadata from data
# ---------------------------
from datetime import datetime, timedelta

# Calculate profile generation date (assuming data is current)
df['profile_date'] = datetime.now().strftime('%Y-%m-%d')

# Calculate data coverage period from financial history (not birth dates)
# Use credit history and employment start dates to determine data range
if 'first_credit_days' in df.columns and 'DAYS_EMPLOYED' in df.columns:
    # Get the oldest financial data point (excluding birth which goes too far back)
    # Focus on actual financial records: credit history and employment
    financial_history_cols = ['first_credit_days', 'DAYS_EMPLOYED']
    
    # Filter out unrealistic values (0 or very extreme values)
    oldest_financial_days = df[financial_history_cols].replace(0, np.nan).min().min()
    
    # Convert to years - but cap at reasonable range (e.g., max 10 years of history)
    if pd.notna(oldest_financial_days) and oldest_financial_days < 0:
        history_years = min(int(abs(oldest_financial_days) / 365), 10)  # Cap at 10 years
        end_year = 2018  # Typical application year for this dataset
        start_year = end_year - history_years
    else:
        start_year = 2015
        end_year = 2018
    
    df['data_period'] = f"{start_year}-{end_year}"
else:
    df['data_period'] = '2015-2018'  # Default reasonable range

print(f"\nTemporal metadata added:")
print(f"  Profile date: {df['profile_date'].iloc[0]}")
print(f"  Data period: {df['data_period'].iloc[0]}")

# ---------------------------
# 7️⃣ Fill missing values intelligently
# ---------------------------
# Fill numeric columns with 0
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# Fill categorical columns with 'Unknown'
categorical_cols = df.select_dtypes(include=['object']).columns
df[categorical_cols] = df[categorical_cols].fillna('Unknown')

# ---------------------------
# 8️⃣ Validate critical columns
# ---------------------------
critical_cols = ['AMT_CREDIT', 'AMT_ANNUITY', 'AMT_INCOME_TOTAL', 'AMT_GOODS_PRICE']
print(f"\nValidating critical columns...")
for col in critical_cols:
    if col in df.columns:
        print(f"  ✓ {col}: {df[col].notna().sum():,} non-null values")
    else:
        print(f"  ✗ {col}: MISSING!")

print(f"\nColumn name check:")
credit_cols = [c for c in df.columns if 'AMT_CREDIT' in c or 'AMT_ANNUITY' in c]
print(f"  Credit/Annuity columns: {credit_cols}")

# ---------------------------
# ✅ df is ready
# ---------------------------
print(f"\n{'='*80}")
print(f"Final dataset shape: {df.shape}")
print(f"{'='*80}")
print(df.head())

# ---------------------------
# 9️⃣ Save merged dataset
# ---------------------------
output_path = "data/processed/merged_data.csv"
df.to_csv(output_path, index=False)
print(f"\n✅ Merged dataset saved to {output_path}")
