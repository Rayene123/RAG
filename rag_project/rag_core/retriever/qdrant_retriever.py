from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

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
            filter_conditions (dict): Optional filters (e.g., {'target': 1, 'CODE_GENDER': 'F', 'DAYS_BIRTH_range': {'gte': -12000}})
        
        Returns:
            list: List of search results with scores and metadata
        """
        # Generate query embedding
        query_vector = self.model.encode(query).tolist()
        
        # Build Qdrant filter if conditions provided
        query_filter = None
        if filter_conditions:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
            
            # Build must conditions
            must_conditions = []
            for key, value in filter_conditions.items():
                # Handle range filters (e.g., DAYS_BIRTH_range, AMT_INCOME_TOTAL_range)
                if key.endswith('_range') and isinstance(value, dict):
                    field_name = key.replace('_range', '')
                    range_filter = Range(
                        gte=value.get('gte'),
                        lte=value.get('lte')
                    )
                    must_conditions.append(
                        FieldCondition(key=field_name, range=range_filter)
                    )
                # Handle exact match filters
                else:
                    must_conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            
            query_filter = Filter(must=must_conditions)
        
        # Search in Qdrant
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter
        ).points
        
        # Format results - include ALL payload data
        results = []
        for hit in search_result:
            result = {
                'client_id': hit.payload.get('client_id'),
                'score': hit.score,
                'target': hit.payload.get('target'),
                'text': hit.payload.get('text'),
                'payload': hit.payload,  # Include full payload
                'metadata': hit.payload  # Also as 'metadata' for compatibility
            }
            results.append(result)
        
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
    
    def get_client_by_id(self, client_id):
        """
        Retrieve a specific client profile by ID
        
        Args:
            client_id (int): Client ID to retrieve
        
        Returns:
            dict: Client profile with metadata, or None if not found
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Search by client_id in payload
        search_result = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="client_id", match=MatchValue(value=client_id))]
            ),
            limit=1
        )
        
        if not search_result[0]:  # scroll returns (points, next_offset)
            return None
        
        point = search_result[0][0]
        return {
            'client_id': point.payload.get('client_id'),
            'target': point.payload.get('target'),
            'text': point.payload.get('text'),
            'payload': point.payload,
            'metadata': point.payload
        }
    
    def get_clients_by_ids(self, client_ids):
        """
        Retrieve multiple client profiles by IDs
        
        Args:
            client_ids (list): List of client IDs to retrieve
        
        Returns:
            list: List of client profiles
        """
        from qdrant_client.models import Filter, FieldCondition, MatchAny
        
        # Search by client_id list
        search_result = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="client_id", match=MatchAny(any=client_ids))]
            ),
            limit=len(client_ids)
        )
        
        results = []
        for point in search_result[0]:  # scroll returns (points, next_offset)
            results.append({
                'client_id': point.payload.get('client_id'),
                'target': point.payload.get('target'),
                'text': point.payload.get('text'),
                'payload': point.payload,
                'metadata': point.payload
            })
        
        return results
    
    def list_clients(self, offset=0, limit=10, filter_conditions=None):
        """
        List clients with pagination and optional filters
        
        Args:
            offset (int): Number of clients to skip
            limit (int): Maximum number of clients to return
            filter_conditions (dict): Optional filters (same format as search())
        
        Returns:
            dict: {'clients': [...], 'total': int, 'offset': int, 'limit': int}
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
        
        # Build filter if provided
        scroll_filter = None
        if filter_conditions:
            must_conditions = []
            for key, value in filter_conditions.items():
                if key.endswith('_range') and isinstance(value, dict):
                    field_name = key.replace('_range', '')
                    range_filter = Range(
                        gte=value.get('gte'),
                        lte=value.get('lte')
                    )
                    must_conditions.append(
                        FieldCondition(key=field_name, range=range_filter)
                    )
                else:
                    must_conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            
            scroll_filter = Filter(must=must_conditions)
        
        # Scroll through collection
        search_result = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=scroll_filter,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False  # Don't need vectors for listing
        )
        
        clients = []
        for point in search_result[0]:  # scroll returns (points, next_offset)
            clients.append({
                'client_id': point.payload.get('client_id'),
                'target': point.payload.get('target'),
                'text': point.payload.get('text'),
                'payload': point.payload,
                'metadata': point.payload
            })
        
        # Get total count (approximate from collection stats)
        collection_info = self.client.get_collection(self.collection_name)
        
        return {
            'clients': clients,
            'total': collection_info.points_count,
            'offset': offset,
            'limit': limit,
            'returned': len(clients)
        }
    
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
    query = "Find clients with high income who own property and have good payment history and their loan requests were approved"
    results = retriever.search(query, top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
        print(f"Client ID: {result['client_id']}")
        print(f"Target: {'Default Risk' if result['target'] == 1 else 'Good Standing'}")
        print(f"\n{result['text']}...")
    
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
        print(f"Target: {'Loan REJECTED (Default Risk)' if result['target'] == 1 else 'Loan APPROVED (Good Standing)'}")
        print(f"\n{result['text'][:500]}...")  # Show first 500 chars
