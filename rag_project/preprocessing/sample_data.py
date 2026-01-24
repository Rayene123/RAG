import pandas as pd
import numpy as np

# ---------------------------
# 1️⃣ Load full dataset
# ---------------------------
print("Loading full dataset...")
features = pd.read_csv("data/processed/features_for_rag.csv")
metadata = pd.read_csv("data/processed/metadata_for_rag.csv")

print(f"Original size: {len(features):,} rows")

# ---------------------------
# 2️⃣ Configuration
# ---------------------------
SAMPLE_SIZE = 10000  # Adjust this number (5k-20k is good for RAG)
STRATIFY = True      # Keep same target distribution

# ---------------------------
# 3️⃣ Sample the data
# ---------------------------
if STRATIFY and 'TARGET' in metadata.columns:
    # Stratified sampling to keep target distribution
    print(f"\nOriginal target distribution:")
    print(metadata['TARGET'].value_counts(normalize=True))
    
    # Merge to get target
    df_full = features.merge(metadata[['SK_ID_CURR', 'TARGET']], on='SK_ID_CURR')
    
    # Sample with stratification
    df_sampled = df_full.groupby('TARGET', group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), SAMPLE_SIZE // 2), random_state=42)
    ).reset_index(drop=True)
    
    # Separate back
    features_sampled = df_sampled.drop(columns=['TARGET'])
    metadata_sampled = metadata[metadata['SK_ID_CURR'].isin(df_sampled['SK_ID_CURR'])]
    
    print(f"\nSampled target distribution:")
    print(metadata_sampled['TARGET'].value_counts(normalize=True))
else:
    # Random sampling
    sample_indices = np.random.choice(len(features), SAMPLE_SIZE, replace=False)
    features_sampled = features.iloc[sample_indices].reset_index(drop=True)
    metadata_sampled = metadata.iloc[sample_indices].reset_index(drop=True)

print(f"\n✅ Sampled size: {len(features_sampled):,} rows")

# ---------------------------
# 4️⃣ Save sampled datasets
# ---------------------------
features_sampled.to_csv("data/processed/features_for_rag_sampled.csv", index=False)
metadata_sampled.to_csv("data/processed/metadata_for_rag_sampled.csv", index=False)

# Calculate size reduction
original_size = (features.memory_usage(deep=True).sum() + metadata.memory_usage(deep=True).sum()) / 1024**2
sampled_size = (features_sampled.memory_usage(deep=True).sum() + metadata_sampled.memory_usage(deep=True).sum()) / 1024**2

print(f"\n📁 Files saved:")
print(f"  - data/processed/features_for_rag_sampled.csv ({len(features_sampled):,} rows)")
print(f"  - data/processed/metadata_for_rag_sampled.csv ({len(metadata_sampled):,} rows)")
print(f"\n💾 Size reduction: {original_size:.1f} MB → {sampled_size:.1f} MB ({sampled_size/original_size*100:.1f}%)")
print(f"\n💡 Original files kept at:")
print(f"  - data/processed/features_for_rag.csv ({len(features):,} rows)")
print(f"  - data/processed/metadata_for_rag.csv ({len(metadata):,} rows)")
