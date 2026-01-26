"""Quick script to check what's stored in Qdrant for a specific client"""
from qdrant_client import QdrantClient
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config.qdrant_config import *

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Check specific client
client_id = 266772

try:
    # Retrieve the point by ID
    point = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[client_id]
    )
    
    if point:
        p = point[0]
        print(f"\n{'='*60}")
        print(f"CLIENT ID: {client_id}")
        print(f"{'='*60}")
        print(f"Point ID: {p.id}")
        print(f"\nPayload:")
        for key, value in p.payload.items():
            if key == 'text':
                print(f"  {key}: {value[:200]}...")  # Truncate text
            else:
                print(f"  {key}: {value}")
        
        print(f"\n{'='*60}")
        print(f"TARGET VALUE: {p.payload.get('target')}")
        print(f"Interpretation: {'Loan REJECTED (Default Risk)' if p.payload.get('target') == 1 else 'Loan APPROVED (Good Standing)'}")
        print(f"{'='*60}")
    else:
        print(f"❌ Client {client_id} not found in Qdrant")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Also check CSV
print(f"\n\nChecking CSV file...")
import pandas as pd
csv_path = TEXT_DATA_PATH
df = pd.read_csv(csv_path)
row = df[df['SK_ID_CURR'] == client_id]

if not row.empty:
    print(f"\n{'='*60}")
    print(f"CSV DATA for Client {client_id}")
    print(f"{'='*60}")
    print(f"TARGET in CSV: {row['TARGET'].values[0]}")
    print(f"{'='*60}")
else:
    print(f"❌ Client {client_id} not found in CSV")
