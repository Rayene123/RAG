import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.qdrant_config import *

# ---------------------------
# 1️⃣ Initialize Qdrant client
# ---------------------------
print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# ---------------------------
# 2️⃣ Create collection
# ---------------------------
try:
    # Delete existing collection if it exists
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"Deleted existing collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"No existing collection to delete")

# Create new collection
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
)
print(f"✅ Created collection: {COLLECTION_NAME}")

# ---------------------------
# 3️⃣ Load embedding model
# ---------------------------
print(f"\nLoading embedding model: {EMBEDDING_MODEL}...")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"✅ Model loaded (dimension: {EMBEDDING_DIMENSION})")

# ---------------------------
# 4️⃣ Load text data and metadata
# ---------------------------
print(f"\nLoading text data from: {TEXT_DATA_PATH}...")
df_text = pd.read_csv(TEXT_DATA_PATH)
print(f"✅ Loaded {len(df_text):,} client descriptions")

# Load original processed data for metadata fields
print(f"\nLoading metadata from: data/processed/features_for_rag_sampled.csv...")
df_metadata = pd.read_csv("data/processed/features_for_rag_sampled.csv")
print(f"✅ Loaded {len(df_metadata):,} client metadata records")

# Merge text with metadata
df = df_text.merge(df_metadata, on='SK_ID_CURR', how='left', suffixes=('', '_meta'))
# Drop duplicate TARGET column if exists
if 'TARGET_meta' in df.columns:
    df = df.drop(columns=['TARGET_meta'])
print(f"✅ Merged text with metadata: {len(df):,} records")

# ---------------------------
# 5️⃣ Generate embeddings and upload to Qdrant
# ---------------------------
print(f"\nGenerating embeddings and uploading to Qdrant...")
points = []

for idx in tqdm(range(0, len(df), BATCH_SIZE), desc="Processing batches"):
    batch = df.iloc[idx:idx + BATCH_SIZE]
    
    # Generate embeddings for batch
    texts = batch['text_description'].tolist()
    embeddings = model.encode(texts, show_progress_bar=False)
    
    # Create points for Qdrant
    for i, (_, row) in enumerate(batch.iterrows()):
        # Build payload with filterable metadata fields
        payload = {
            'client_id': int(row['SK_ID_CURR']),
            'target': int(row['TARGET']),
            'text': row['text_description'],
            # Categorical fields (exact match)
            'CODE_GENDER': str(row.get('CODE_GENDER', 'Unknown')),
            'NAME_FAMILY_STATUS': str(row.get('NAME_FAMILY_STATUS', 'Unknown')),
            'NAME_EDUCATION_TYPE': str(row.get('NAME_EDUCATION_TYPE', 'Unknown')),
            'NAME_INCOME_TYPE': str(row.get('NAME_INCOME_TYPE', 'Unknown')),
            'FLAG_OWN_CAR': str(row.get('FLAG_OWN_CAR', 'N')),
            'FLAG_OWN_REALTY': str(row.get('FLAG_OWN_REALTY', 'N')),
            'NAME_HOUSING_TYPE': str(row.get('NAME_HOUSING_TYPE', 'Unknown')),
            'OCCUPATION_TYPE': str(row.get('OCCUPATION_TYPE', 'Unknown')),
            'NAME_CONTRACT_TYPE': str(row.get('NAME_CONTRACT_TYPE', 'Unknown')),
            # Numeric fields (range filtering)
            'CNT_CHILDREN': int(row.get('CNT_CHILDREN', 0)) if pd.notna(row.get('CNT_CHILDREN')) else 0,
            'CNT_FAM_MEMBERS': int(row.get('CNT_FAM_MEMBERS', 0)) if pd.notna(row.get('CNT_FAM_MEMBERS')) else 0,
            'DAYS_BIRTH': int(row.get('DAYS_BIRTH', 0)) if pd.notna(row.get('DAYS_BIRTH')) else 0,
            'DAYS_EMPLOYED': int(row.get('DAYS_EMPLOYED', 0)) if pd.notna(row.get('DAYS_EMPLOYED')) else 0,
            'AMT_INCOME_TOTAL': float(row.get('AMT_INCOME_TOTAL', 0)) if pd.notna(row.get('AMT_INCOME_TOTAL')) else 0.0,
            'AMT_CREDIT': float(row.get('AMT_CREDIT', 0)) if pd.notna(row.get('AMT_CREDIT', 0)) else 0.0,
            'OWN_CAR_AGE': float(row.get('OWN_CAR_AGE', 0)) if pd.notna(row.get('OWN_CAR_AGE')) else 0.0,
        }
        
        point = PointStruct(
            id=int(row['SK_ID_CURR']),
            vector=embeddings[i].tolist(),
            payload=payload
        )
        points.append(point)
    
    # Upload batch to Qdrant
    if len(points) >= 100:  # Upload in chunks of 100
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        points = []

# Upload remaining points
if points:
    client.upsert(collection_name=COLLECTION_NAME, points=points)

# ---------------------------
# 6️⃣ Verify collection
# ---------------------------
collection_info = client.get_collection(collection_name=COLLECTION_NAME)
print(f"\n✅ Ingestion complete!")
print(f"Collection: {COLLECTION_NAME}")
print(f"Total vectors: {collection_info.points_count}")
print(f"Vector dimension: {EMBEDDING_DIMENSION}")
print(f"Distance metric: COSINE")
