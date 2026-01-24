# Qdrant Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "credit_clients"

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast, good quality
# Alternative models:
# "sentence-transformers/all-mpnet-base-v2"  # Higher quality, slower
# "BAAI/bge-small-en-v1.5"  # Good balance

EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2
BATCH_SIZE = 32

# Data paths
TEXT_DATA_PATH = "data/processed/client_texts_for_embedding.csv"
