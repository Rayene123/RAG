# Qdrant Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "credit_clients"

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIMENSION = 768
BATCH_SIZE = 32

# Data paths
TEXT_DATA_PATH = "data/processed/client_texts_for_embedding.csv"
