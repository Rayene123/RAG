from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import sys
sys.path.append('..')
from config.qdrant_config import *

class QdrantRetriever:
    """Retriever for querying Qdrant vector database"""
    
    def __init__(self, host=QDRANT_HOST, port=QDRANT_PORT, 
                 collection_name=COLLECTION_NAME, model_name=EMBEDDING_MODEL):
        """Initialize Qdrant client and embedding model"""
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.model = SentenceTransformer(model_name)
        print(f"✅ QdrantRetriever initialized")
        print(f"   Collection: {collection_name}")
        print(f"   Model: {model_name}")
    
    def search(self, query, top_k=5, filter_conditions=None):
        """
        Search for similar clients based on natural language query
        
        Args:
            query (str): Natural language search query
            top_k (int): Number of results to return
            filter_conditions (dict): Optional filters (e.g., {'target': 1})
        
        Returns:
            list: List of search results with scores and metadata
        """
        # Generate query embedding
        query_vector = self.model.encode(query).tolist()
        
        # Search in Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=filter_conditions
        )
        
        # Format results
        results = []
        for hit in search_result:
            results.append({
                'client_id': hit.payload['client_id'],
                'score': hit.score,
                'target': hit.payload['target'],
                'text': hit.payload['text']
            })
        
        return results
    
    def search_by_client_profile(self, age=None, income=None, education=None, 
                                   occupation=None, top_k=5):
        """
        Search for similar clients based on profile attributes
        
        Args:
            age (int): Client age
            income (float): Annual income
            education (str): Education level
            occupation (str): Occupation type
            top_k (int): Number of results
        
        Returns:
            list: List of similar clients
        """
        # Build query from attributes
        query_parts = []
        if age:
            query_parts.append(f"{age} years old")
        if income:
            query_parts.append(f"income ${income:,.0f}")
        if education:
            query_parts.append(f"education {education}")
        if occupation:
            query_parts.append(f"occupation {occupation}")
        
        query = "Client profile: " + ", ".join(query_parts)
        return self.search(query, top_k=top_k)
    
    def get_collection_stats(self):
        """Get statistics about the collection"""
        collection_info = self.client.get_collection(self.collection_name)
        return {
            'total_vectors': collection_info.points_count,
            'vector_dimension': collection_info.config.params.vectors.size,
            'distance_metric': collection_info.config.params.vectors.distance
        }


# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    # Initialize retriever
    retriever = QdrantRetriever()
    
    # Get stats
    stats = retriever.get_collection_stats()
    print(f"\nCollection Stats:")
    print(f"  Total vectors: {stats['total_vectors']}")
    print(f"  Dimension: {stats['vector_dimension']}")
    
    # Example search 1: Natural language query
    print("\n" + "="*80)
    print("Example 1: Natural language search")
    print("="*80)
    query = "Find clients with high income who own property and have good payment history"
    results = retriever.search(query, top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
        print(f"Client ID: {result['client_id']}")
        print(f"Target: {'Default Risk' if result['target'] == 1 else 'Good Standing'}")
        print(f"\n{result['text'][:400]}...")
    
    # Example search 2: Profile-based search
    print("\n" + "="*80)
    print("Example 2: Profile-based search")
    print("="*80)
    results = retriever.search_by_client_profile(
        age=35,
        income=50000,
        education="Higher education",
        top_k=3
    )
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
        print(f"Client ID: {result['client_id']}")
