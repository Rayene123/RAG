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
# 4️⃣ Load text data
# ---------------------------
print(f"\nLoading text data from: {TEXT_DATA_PATH}...")
df = pd.read_csv(TEXT_DATA_PATH)
print(f"✅ Loaded {len(df):,} client descriptions")

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
        point = PointStruct(
            id=int(row['SK_ID_CURR']),
            vector=embeddings[i].tolist(),
            payload={
                'client_id': int(row['SK_ID_CURR']),
                'target': int(row['TARGET']),
                'text': row['text_description']
            }
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
