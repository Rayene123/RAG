import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import os

# ---------------------------
# 1️⃣ Load merged dataset
# ---------------------------
df = pd.read_csv("data/processed/merged_data.csv")

# ---------------------------
# 2️⃣ Select key features for text-based RAG
# ---------------------------
print("Selecting features for text-based RAG...")

# Key numeric features (most informative for credit risk)
numeric_cols = [
    'AMT_INCOME_TOTAL', 'AMT_CREDIT_x', 'AMT_ANNUITY_x', 'AMT_GOODS_PRICE',
    'DAYS_BIRTH', 'DAYS_EMPLOYED', 'CNT_CHILDREN', 'CNT_FAM_MEMBERS',
    'avg_payment_delay', 'payment_ratio',
    'nb_active_credits', 'total_external_credit', 'total_external_debt',
    'sum_overdue_amount', 'current_overdue_days'
]

# Key categorical features (will be converted to text later)
categorical_cols = [
    'NAME_CONTRACT_TYPE', 'CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY',
    'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 'NAME_FAMILY_STATUS',
    'NAME_HOUSING_TYPE', 'OCCUPATION_TYPE'
]

# Only include columns that exist in the dataframe
numeric_cols = [col for col in numeric_cols if col in df.columns]
categorical_cols = [col for col in categorical_cols if col in df.columns]

print(f"Selected {len(numeric_cols)} numeric and {len(categorical_cols)} categorical features")
print(f"Total features: {len(numeric_cols) + len(categorical_cols)}")

id_cols = ['SK_ID_CURR']

# ---------------------------
# 3️⃣ Add placeholders for documents (text/pdf/images)
# ---------------------------
# These columns will hold paths or references to actual documents for RAG
doc_cols = ['text_path', 'pdf_path', 'image_path']
for col in doc_cols:
    df[col] = ""  # Fill later with actual file paths or URLs

# ---------------------------
# 4️⃣ Create features dataframe (keep categoricals as text)
# ---------------------------
# Combine ID, numeric, and categorical features (NO one-hot encoding)
features_df = df[id_cols + numeric_cols + categorical_cols].copy()

# Fill missing categorical values
for col in categorical_cols:
    features_df[col] = features_df[col].fillna('Unknown')

print(f"Features ready for text conversion: {features_df.shape}")

# ---------------------------
# 5️⃣ Normalize numeric columns (keep in separate columns for text generation)
# ---------------------------
# Handle inf and NaN values before scaling
features_df[numeric_cols] = features_df[numeric_cols].replace([np.inf, -np.inf], np.nan)
features_df[numeric_cols] = features_df[numeric_cols].fillna(0)

# Create normalized versions (with _norm suffix) for embeddings if needed
scaler = MinMaxScaler()
normalized_values = scaler.fit_transform(features_df[numeric_cols])
for i, col in enumerate(numeric_cols):
    features_df[f'{col}_norm'] = normalized_values[:, i]

print(f"Normalized {len(numeric_cols)} numeric features")

# ---------------------------
# 6️⃣ Separate metadata
# ---------------------------
metadata = df[id_cols + doc_cols + ['TARGET']].copy()  # Keep ID, document links, and target

# ---------------------------
# 7️⃣ Save processed features and metadata
# ---------------------------
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/metadata", exist_ok=True)

features_df.to_csv("data/processed/features_for_rag.csv", index=False)
metadata.to_csv("data/processed/metadata_for_rag.csv", index=False)

# ---------------------------
# 8️⃣ Save data dictionary to metadata folder
# ---------------------------
data_dict = {
    'numeric_features': {col: {
        'description': col.replace('_', ' ').title(),
        'type': 'numeric',
        'normalized': f'{col}_norm' in features_df.columns
    } for col in numeric_cols},
    'categorical_features': {col: {
        'description': col.replace('_', ' ').title(),
        'type': 'categorical',
        'unique_values': df[col].nunique() if col in df.columns else 0
    } for col in categorical_cols},
    'total_records': len(features_df),
    'total_features': len(numeric_cols) + len(categorical_cols)
}

import json
with open('data/metadata/feature_dictionary.json', 'w') as f:
    json.dump(data_dict, f, indent=2)

print("\n✅ Preprocessing done!")
print(f"Features shape: {features_df.shape}")
print(f"  - Numeric features: {len(numeric_cols)} (raw + normalized)")
print(f"  - Categorical features: {len(categorical_cols)} (as text)")
print(f"Metadata shape: {metadata.shape}")
print(f"\n📁 Files saved:")
print(f"  - data/processed/features_for_rag.csv")
print(f"  - data/processed/metadata_for_rag.csv")
print(f"  - data/metadata/feature_dictionary.json")
