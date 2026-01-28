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
from rag_core.utils.feature_extractor import FeatureExtractor

# Resolve absolute data paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_DATA_PATH_ABS = os.path.join(PROJECT_ROOT, TEXT_DATA_PATH)
METADATA_PATH_ABS = os.path.join(PROJECT_ROOT, "data/processed/metadata_for_rag_sampled.csv")

# ---------------------------
# 1️⃣ Initialize Qdrant client
# ---------------------------
# Prefer cloud if environment variables are set
cloud_url = os.getenv("API_QDRANT_URL")
cloud_key = os.getenv("API_QDRANT_API_KEY")
if cloud_url:
    print(f"Connecting to Qdrant Cloud at {cloud_url}...")
    client = QdrantClient(url=cloud_url, api_key=cloud_key or None)
else:
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

# Create payload indexes for all filterable fields (required in Qdrant Cloud)
from qdrant_client.models import PayloadSchemaType

# Define all fields that need indexes
index_fields = [
    ("client_id", PayloadSchemaType.INTEGER),
    ("target", PayloadSchemaType.INTEGER),
    ("CODE_GENDER", PayloadSchemaType.KEYWORD),
    ("NAME_FAMILY_STATUS", PayloadSchemaType.KEYWORD),
    ("NAME_EDUCATION_TYPE", PayloadSchemaType.KEYWORD),
    ("NAME_INCOME_TYPE", PayloadSchemaType.KEYWORD),
    ("FLAG_OWN_CAR", PayloadSchemaType.KEYWORD),
    ("FLAG_OWN_REALTY", PayloadSchemaType.KEYWORD),
    ("NAME_HOUSING_TYPE", PayloadSchemaType.KEYWORD),
    ("OCCUPATION_TYPE", PayloadSchemaType.KEYWORD),
    ("NAME_CONTRACT_TYPE", PayloadSchemaType.KEYWORD),
    ("CNT_CHILDREN", PayloadSchemaType.INTEGER),
    ("CNT_FAM_MEMBERS", PayloadSchemaType.INTEGER),
    ("DAYS_BIRTH", PayloadSchemaType.INTEGER),
    ("DAYS_EMPLOYED", PayloadSchemaType.INTEGER),
    ("AMT_INCOME_TOTAL", PayloadSchemaType.FLOAT),
    ("AMT_CREDIT", PayloadSchemaType.FLOAT),
    ("OWN_CAR_AGE", PayloadSchemaType.FLOAT),
    ("EXTERNAL_CREDIT_AMOUNT", PayloadSchemaType.FLOAT),
    ("MONTHLY_ANNUITY", PayloadSchemaType.FLOAT),
    ("APPROVAL_RATE", PayloadSchemaType.FLOAT),
    ("ACTIVE_EXTERNAL_CREDITS", PayloadSchemaType.INTEGER),
]

print(f"\nCreating payload indexes for {len(index_fields)} fields...")
for field_name, field_schema in index_fields:
    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field_name,
            field_schema=field_schema
        )
        print(f"  ✅ Index created: {field_name} ({field_schema})")
    except Exception as e:
        print(f"  ⚠️  {field_name}: {e}")

# ---------------------------
# 3️⃣ Load embedding model
# ---------------------------
print(f"\nLoading embedding model: {EMBEDDING_MODEL}...")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"✅ Model loaded (dimension: {EMBEDDING_DIMENSION})")

# ---------------------------
# 4️⃣ Load text data and metadata
# ---------------------------
print(f"\nLoading text data from: {TEXT_DATA_PATH_ABS}...")
df_text = pd.read_csv(TEXT_DATA_PATH_ABS)
print(f"✅ Loaded {len(df_text):,} client descriptions")

# Load original processed data for metadata fields
print(f"\nLoading metadata from: {METADATA_PATH_ABS}...")
df_metadata = pd.read_csv(METADATA_PATH_ABS)
print(f"✅ Loaded {len(df_metadata):,} client metadata records")

# Merge text with metadata
df = df_text.merge(df_metadata, on='SK_ID_CURR', how='left', suffixes=('', '_meta'))
# Drop duplicate TARGET column if exists
if 'TARGET_meta' in df.columns:
    df = df.drop(columns=['TARGET_meta'])
print(f"✅ Merged text with metadata: {len(df):,} records")
print(f"✅ Processing all {len(df):,} records for ingestion")

# ---------------------------
# 5️⃣ Generate embeddings and upload to Qdrant
# ---------------------------
print(f"\nGenerating embeddings and uploading to Qdrant...")
points = []
fe = FeatureExtractor()

for idx in tqdm(range(0, len(df), BATCH_SIZE), desc="Processing batches"):
    batch = df.iloc[idx:idx + BATCH_SIZE]
    
    # Generate embeddings for batch
    texts = batch['text_description'].tolist()
    embeddings = model.encode(texts, show_progress_bar=False)
    
    # Create points for Qdrant
    for i, (_, row) in enumerate(batch.iterrows()):
        text = row['text_description']
        summary = fe.extract_summary(text)
        # Build payload with filterable metadata fields (prefer parsed text values)
        payload = {
            'client_id': int(row['SK_ID_CURR']),
            'target': int(row['TARGET']),
            'text': text,
            # Categorical fields
            'CODE_GENDER': summary.get('gender') or str(row.get('CODE_GENDER', 'Unknown')),
            'NAME_FAMILY_STATUS': str(row.get('NAME_FAMILY_STATUS', 'Unknown')),
            'NAME_EDUCATION_TYPE': summary.get('education') or str(row.get('NAME_EDUCATION_TYPE', 'Unknown')),
            'NAME_INCOME_TYPE': summary.get('income_type') or str(row.get('NAME_INCOME_TYPE', 'Unknown')),
            'FLAG_OWN_CAR': ('Y' if summary.get('owns_car') else 'N') if summary.get('owns_car') is not None else str(row.get('FLAG_OWN_CAR', 'N')),
            'FLAG_OWN_REALTY': ('Y' if summary.get('owns_realty') else 'N') if summary.get('owns_realty') is not None else str(row.get('FLAG_OWN_REALTY', 'N')),
            'NAME_HOUSING_TYPE': str(row.get('NAME_HOUSING_TYPE', 'Unknown')),
            'OCCUPATION_TYPE': summary.get('occupation') or str(row.get('OCCUPATION_TYPE', 'Unknown')),
            'NAME_CONTRACT_TYPE': summary.get('contract_type') or str(row.get('NAME_CONTRACT_TYPE', 'Unknown')),
            # Numeric fields
            'CNT_CHILDREN': summary.get('children', int(row.get('CNT_CHILDREN', 0)) if pd.notna(row.get('CNT_CHILDREN')) else 0),
            'CNT_FAM_MEMBERS': int(row.get('CNT_FAM_MEMBERS', 0)) if pd.notna(row.get('CNT_FAM_MEMBERS')) else 0,
            'DAYS_BIRTH': int(row.get('DAYS_BIRTH', 0)) if pd.notna(row.get('DAYS_BIRTH')) else 0,
            'DAYS_EMPLOYED': summary.get('years_employed', int(row.get('DAYS_EMPLOYED', 0)) if pd.notna(row.get('DAYS_EMPLOYED')) else 0),
            'AMT_INCOME_TOTAL': float(summary.get('annual_income', row.get('AMT_INCOME_TOTAL', 0) or 0.0)),
            'AMT_CREDIT': float(summary.get('requested_credit', row.get('AMT_CREDIT', 0) or 0.0)),
            'OWN_CAR_AGE': float(summary.get('car_age_years', row.get('OWN_CAR_AGE', 0) or 0.0)),
            # Additional derived fields
            'EXTERNAL_CREDIT_AMOUNT': float(summary.get('external_credit_amount', 0.0)),
            'MONTHLY_ANNUITY': float(summary.get('monthly_annuity', 0.0)),
            'APPROVAL_RATE': float(summary.get('approval_rate', 0.0)),
            'ACTIVE_EXTERNAL_CREDITS': int(summary.get('active_external_credits', 0)),
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
