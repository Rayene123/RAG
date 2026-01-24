import pandas as pd
import numpy as np

# ---------------------------
# 1️⃣ Load sampled dataset
# ---------------------------
print("Loading sampled dataset...")
features = pd.read_csv("data/processed/features_for_rag_sampled.csv")
metadata = pd.read_csv("data/processed/metadata_for_rag_sampled.csv")

# Merge for complete info
df = features.merge(metadata, on='SK_ID_CURR')

print(f"Dataset size: {len(df):,} rows")

# ---------------------------
# 2️⃣ Convert each row to text description
# ---------------------------
def create_client_description(row):
    """Convert a client row to human-readable text for embeddings"""
    
    # Parse age from DAYS_BIRTH (negative days)
    age = int(-row['DAYS_BIRTH'] / 365) if pd.notna(row['DAYS_BIRTH']) else 'Unknown'
    
    # Parse employment years
    emp_years = int(-row['DAYS_EMPLOYED'] / 365) if pd.notna(row['DAYS_EMPLOYED']) and row['DAYS_EMPLOYED'] < 0 else 'Unknown'
    
    # Format income
    income = f"${row['AMT_INCOME_TOTAL']:,.0f}" if pd.notna(row['AMT_INCOME_TOTAL']) else 'Unknown'
    
    # Format credit amounts
    credit_current = f"${row['AMT_CREDIT_x']:,.0f}" if pd.notna(row['AMT_CREDIT_x']) else 'Unknown'
    annuity = f"${row['AMT_ANNUITY_x']:,.0f}" if pd.notna(row['AMT_ANNUITY_x']) else 'Unknown'
    goods_price = f"${row['AMT_GOODS_PRICE']:,.0f}" if pd.notna(row['AMT_GOODS_PRICE']) else 'Unknown'
    
    # Basic info
    gender = row.get('CODE_GENDER', 'Unknown')
    contract_type = row.get('NAME_CONTRACT_TYPE', 'Unknown')
    income_type = row.get('NAME_INCOME_TYPE', 'Unknown')
    education = row.get('NAME_EDUCATION_TYPE', 'Unknown')
    family_status = row.get('NAME_FAMILY_STATUS', 'Unknown')
    housing = row.get('NAME_HOUSING_TYPE', 'Unknown')
    occupation = row.get('OCCUPATION_TYPE', 'Unknown')
    
    owns_car = 'owns a car' if row.get('FLAG_OWN_CAR') == 'Y' else 'does not own a car'
    owns_realty = 'owns real estate' if row.get('FLAG_OWN_REALTY') == 'Y' else 'does not own real estate'
    
    children = int(row.get('CNT_CHILDREN', 0))
    family_members = int(row.get('CNT_FAM_MEMBERS', 0))
    
    # Credit history
    payment_delay = row.get('avg_payment_delay', 0)
    payment_ratio = row.get('payment_ratio', 0)
    active_credits = int(row.get('nb_active_credits', 0)) if pd.notna(row.get('nb_active_credits')) else 0
    external_debt = f"${row.get('total_external_debt', 0):,.0f}" if pd.notna(row.get('total_external_debt')) else '$0'
    overdue_amount = row.get('sum_overdue_amount', 0)
    overdue_days = int(row.get('current_overdue_days', 0)) if pd.notna(row.get('current_overdue_days')) else 0
    
    # Build description
    description = f"""Client Profile (ID: {row['SK_ID_CURR']}):

Personal Information:
- Age: {age} years old
- Gender: {gender}
- Education: {education}
- Family Status: {family_status}
- Children: {children}, Total family members: {family_members}
- Housing: {housing}

Financial Information:
- Income Type: {income_type}
- Annual Income: {income}
- Occupation: {occupation}
- {owns_car}, {owns_realty}

Current Credit Application:
- Contract Type: {contract_type}
- Credit Amount: {credit_current}
- Annuity: {annuity}
- Goods Price: {goods_price}

Employment:
- Years Employed: {emp_years}

Credit History:
- Active Credits: {active_credits}
- Total External Debt: {external_debt}
- Average Payment Delay: {payment_delay:.1f} days
- Payment Ratio: {payment_ratio:.2%}
- Current Overdue Days: {overdue_days}
- Overdue Amount: ${overdue_amount:,.0f}

Target: {'Default Risk' if row['TARGET'] == 1 else 'Good Standing'}
"""
    
    return description.strip()

# ---------------------------
# 3️⃣ Generate text for all rows
# ---------------------------
print("\nGenerating text descriptions...")
df['text_description'] = df.apply(create_client_description, axis=1)

# ---------------------------
# 4️⃣ Save text descriptions
# ---------------------------
output_df = df[['SK_ID_CURR', 'TARGET', 'text_description']].copy()
output_df.to_csv("data/processed/client_texts_for_embedding.csv", index=False)

# Also save as individual text files (optional, for inspection)
import os
os.makedirs("embeddings/text", exist_ok=True)

# Save first 10 as examples
for i in range(min(10, len(output_df))):
    client_id = output_df.iloc[i]['SK_ID_CURR']
    text = output_df.iloc[i]['text_description']
    with open(f"embeddings/text/client_{client_id}.txt", 'w', encoding='utf-8') as f:
        f.write(text)

print(f"\n✅ Text conversion complete!")
print(f"📁 Files saved:")
print(f"  - data/processed/client_texts_for_embedding.csv ({len(output_df):,} rows)")
print(f"  - embeddings/text/client_*.txt (first 10 samples)")
print(f"\nSample text preview:")
print("="*80)
print(output_df.iloc[0]['text_description'][:500] + "...")
