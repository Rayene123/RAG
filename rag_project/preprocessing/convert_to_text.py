import pandas as pd
import numpy as np

# ---------------------------
# 1️⃣ Load full dataset (all clients)
# ---------------------------
print("Loading full dataset...")
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
    credit_amount = f"${row.get('AMT_CREDIT', 0):,.0f}" if pd.notna(row.get('AMT_CREDIT')) else 'Unknown'
    annuity = f"${row.get('AMT_ANNUITY', 0):,.0f}" if pd.notna(row.get('AMT_ANNUITY')) else 'Unknown'
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
    external_credit = f"${row.get('total_external_credit', 0):,.0f}" if pd.notna(row.get('total_external_credit')) else '$0'
    external_debt = f"${row.get('total_external_debt', 0):,.0f}" if pd.notna(row.get('total_external_debt')) else '$0'
    overdue_amount = row.get('sum_overdue_amount', 0)
    max_overdue_amount = row.get('max_overdue_amount', 0)
    max_overdue_days = int(row.get('max_overdue_days', 0)) if pd.notna(row.get('max_overdue_days')) else 0
    # Note: max_overdue_days is the max of CREDIT_DAY_OVERDUE (current overdue) across all bureau records
    prolongations = int(row.get('total_prolongations', 0)) if pd.notna(row.get('total_prolongations')) else 0
    
    # Previous application history
    prev_credit = f"${row.get('AMT_CREDIT_prev', 0):,.0f}" if pd.notna(row.get('AMT_CREDIT_prev')) and row.get('AMT_CREDIT_prev', 0) > 0 else None
    prev_annuity = f"${row.get('AMT_ANNUITY_prev', 0):,.0f}" if pd.notna(row.get('AMT_ANNUITY_prev')) and row.get('AMT_ANNUITY_prev', 0) > 0 else None
    status_accepted = row.get('STATUS_ACCEPTED', 0)
    status_refused = row.get('STATUS_REFUSED', 0)
    
    # Additional features
    car_age = int(row.get('OWN_CAR_AGE', 0)) if pd.notna(row.get('OWN_CAR_AGE')) and row.get('OWN_CAR_AGE', 0) > 0 else None

    # Build previous application section
    prev_section = ""
    if prev_credit or status_accepted > 0 or status_refused > 0:
        prev_section = f"""Previous Loan Applications:
- Average Previous Credit Amount: {prev_credit if prev_credit else 'None'}
- Average Previous Annuity: {prev_annuity if prev_annuity else 'None'}
- Approval Rate: {status_accepted:.1%}
- Rejection Rate: {status_refused:.1%}

"""
    else:
        prev_section = """Previous Loan Applications:
- No previous loan history recorded

"""
    
    # Build risk reasoning
    risk_reasons = []
    if max_overdue_days == 0:
        risk_reasons.append("No current overdue payments")
    if payment_ratio >= 0.95:
        risk_reasons.append("Excellent payment completion ratio")
    elif payment_ratio >= 0.80:
        risk_reasons.append("Good payment history")
    if payment_delay <= 0:
        risk_reasons.append("Early or on-time payment pattern")
    elif payment_delay > 30:
        risk_reasons.append("History of late payments")
    if emp_years != 'Unknown' and int(emp_years) >= 5:
        risk_reasons.append("Stable long-term employment")
    if external_debt != '$0' and active_credits > 0:
        try:
            debt_val = float(external_debt.replace('$', '').replace(',', ''))
            credit_val = float(external_credit.replace('$', '').replace(',', ''))
            if credit_val > 0 and debt_val / credit_val < 0.3:
                risk_reasons.append("Low debt relative to total credit")
            elif debt_val / credit_val > 0.7:
                risk_reasons.append("High debt burden")
        except:
            pass
    if max_overdue_days > 30:
        risk_reasons.append("Historical overdue payment issues")
    if max_overdue_amount > 0:
        try:
            income_val = float(income.replace('$', '').replace(',', ''))
            if income_val > 0 and max_overdue_amount / income_val > 0.5:
                risk_reasons.append("Large historical overdue amounts relative to income")
        except:
            pass
    if prolongations > 0:
        risk_reasons.append(f"Has {prolongations} credit prolongation(s)")
    
    if not risk_reasons:
        risk_reasons = ["Standard credit profile"]
    
    risk_reasoning = "\n".join([f"- {reason}" for reason in risk_reasons])
    
    # Build description
    description = f"""Client ID: {row['SK_ID_CURR']}
Document Type: Client Financial Profile
Profile Generated On: 2025-01-03
Data Coverage Period: 2015–2024

Personal Information:
- Age: {age} years
- Gender: {gender}
- Education Level: {education}
- Family Status: {family_status}
- Number of Children: {children}
- Household Size: {family_members}
- Housing Type: {housing}

Assets & Ownership:
- Owns Real Estate: {'Yes' if row.get('FLAG_OWN_REALTY') == 'Y' else 'No'}
- Owns a Car: {'Yes' if row.get('FLAG_OWN_CAR') == 'Y' else 'No'}{f' (age: {car_age} years)' if car_age else ''}

Employment & Income:
- Income Type: {income_type}
- Occupation: {occupation}
- Years Employed: {emp_years}
- Annual Income: {income}

Current Loan Application:
- Contract Type: {contract_type}
- Requested Credit Amount: {credit_amount}
- Monthly Annuity: {annuity}
- Goods Price: {goods_price}

{prev_section}Credit History & Payment Behavior:
- Active External Credits: {active_credits}
- Total External Credit Amount: {external_credit}
- Total Outstanding Debt: {external_debt}
- Average Payment Delay: {payment_delay:.1f} days{' (early payments)' if payment_delay < 0 else ''}
- Payment Completion Ratio: {payment_ratio:.1%}
- Current Overdue Days: {max_overdue_days}
- Historical Maximum Overdue Days: {max_overdue_days}
- Total Credit Prolongations: {prolongations}
- Current Overdue Amount: ${overdue_amount:,.0f}
- Historical Maximum Overdue Amount: ${max_overdue_amount:,.0f}

Risk Assessment:
Status: {'DEFAULT RISK' if row['TARGET'] == 1 else 'GOOD STANDING'}
Reasoning:
{risk_reasoning}
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

# Also save as individual text files
import os
os.makedirs("embeddings/text", exist_ok=True)

# Save ALL clients as individual text files
print("\nSaving individual text files...")
for i in range(len(output_df)):
    client_id = output_df.iloc[i]['SK_ID_CURR']
    text = output_df.iloc[i]['text_description']
    with open(f"embeddings/text/client_{client_id}.txt", 'w', encoding='utf-8') as f:
        f.write(text)
    if (i + 1) % 10000 == 0:
        print(f"  Saved {i + 1:,}/{len(output_df):,} files...")

print(f"\n✅ Text conversion complete!")
print(f"📁 Files saved:")
print(f"  - data/processed/client_texts_for_embedding.csv ({len(output_df):,} rows)")
print(f"  - embeddings/text/client_*.txt ({len(output_df):,} individual files)")
print(f"\nSample text preview:")
print("="*80)
print(output_df.iloc[0]['text_description'][:500] + "...")
