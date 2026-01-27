"""
Query Router for RAG System.

Routes queries based on input type:
- Text queries: Direct to retriever
- PDF files: Transform to text, then to retriever
- Images: Transform to text, then to retriever (future support)
"""

import os
import sys
from pathlib import Path
from typing import Union, List, Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from rag_core.query_processor.transformers.pdf_transformer import PDFTransformer
from rag_core.query_processor.transformers.image_transformer import ImageTransformer
from rag_core.retriever.qdrant_retriever import QdrantRetriever
from rag_core.utils.feature_extractor import FeatureExtractor
from rag_core.query_processor.llm_query_understanding import LLMQueryUnderstanding


class QueryRouter:
    """
    Routes queries to appropriate processing pipeline based on input type.
    """
    
    def __init__(self, retriever: QdrantRetriever = None, use_llm_understanding: bool = True):
        """
        Initialize Query Router.
        
        Args:
            retriever: QdrantRetriever instance. If None, creates a new one.
            use_llm_understanding: Use LLM for query understanding (default: True)
        """
        # Initialize retriever
        self.retriever = retriever if retriever else QdrantRetriever()
        
        # Initialize transformers (lazy loading)
        self._pdf_transformer = None
        self._image_transformer = None
        
        # Initialize feature extractor
        self.feature_extractor = FeatureExtractor()
        
        # Initialize query understanding (LLM-based)
        self.use_llm_understanding = use_llm_understanding
        if use_llm_understanding:
            try:
                self.query_understanding = LLMQueryUnderstanding(llm_provider="mistral")
                print("✅ QueryRouter initialized (LLM-based understanding)")
            except Exception as e:
                print(f"⚠️  Failed to initialize LLM understanding: {e}")
                print("   Query understanding disabled, will use direct search")
                self.query_understanding = None
                self.use_llm_understanding = False
                print("✅ QueryRouter initialized (no query understanding)")
        else:
            self.query_understanding = None
            print("✅ QueryRouter initialized (no query understanding)")
    
    @property
    def pdf_transformer(self):
        """Lazy load PDF transformer"""
        if self._pdf_transformer is None:
            self._pdf_transformer = PDFTransformer()
            print("   📄 PDF transformer loaded")
        return self._pdf_transformer
    
    @property
    def image_transformer(self):
        """Lazy load image transformer"""
        if self._image_transformer is None:
            self._image_transformer = ImageTransformer()
            print("   🖼️  Image transformer loaded")
        return self._image_transformer
    
    def detect_query_type(self, query: Union[str, Path]) -> str:
        """
        Detect the type of query input.
        
        Args:
            query: String query or file path
        
        Returns:
            str: 'text', 'pdf', or 'image'
        """
        # If it's a string, check if it's a file path
        if isinstance(query, str):
            # Check if it looks like a file path
            if os.path.exists(query):
                query_path = Path(query)
            else:
                # It's a text query
                return 'text'
        elif isinstance(query, Path):
            query_path = query
        else:
            return 'text'
        
        # Check file extension
        if query_path.suffix.lower() == '.pdf':
            return 'pdf'
        elif query_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            return 'image'
        else:
            return 'text'
    
    def process_text_query(self, query: str, top_k: int = 5, 
                          filter_conditions: Dict = None,
                          enable_query_understanding: bool = True) -> List[Dict[str, Any]]:
        """
        Process a text query directly.
        
        Args:
            query: Natural language query string
            top_k: Number of results to return
            filter_conditions: Optional filters for search
            enable_query_understanding: Whether to parse query for intent (default: True)
        
        Returns:
            List of search results
        """
        # Parse query for intent if enabled and available
        if enable_query_understanding and self.query_understanding:
            parsed = self.query_understanding.parse_query(query)
            
            # Show what was understood
            if parsed['detected_filters']:
                print(f"🧠 Query Understanding:")
                for f in parsed['detected_filters']:
                    print(f"   - {f}")
            
            # Show filters being applied
            if parsed.get('filters'):
                print(f"🔍 Applying Filters:")
                for key, value in parsed['filters'].items():
                    if isinstance(value, dict):
                        print(f"   - {key}: {value}")
                    else:
                        print(f"   - {key}: {value}")
            
            # Use cleaned query for search
            search_query = parsed['search_query'] if parsed['search_query'] else query
            
            # Merge parsed filters with explicit filters
            final_filters = filter_conditions.copy() if filter_conditions else {}
            final_filters.update(parsed['filters'])
        else:
            search_query = query
            final_filters = filter_conditions
        
        print(f"📝 Processing text query: '{search_query[:50]}...'")
        results = self.retriever.search(search_query, top_k=top_k, 
                                       filter_conditions=final_filters)
        print(f"   Found {len(results)} results")
        return results
    
    def process_pdf_query(self, pdf_path: Union[str, Path], top_k: int = 5,
                         filter_conditions: Dict = None) -> List[Dict[str, Any]]:
        """
        Process a PDF file query.
        
        Steps:
        1. Transform PDF to text
        2. Use extracted text for retrieval
        
        Args:
            pdf_path: Path to PDF file
            top_k: Number of results to return
            filter_conditions: Optional filters for search
        
        Returns:
            List of search results with PDF metadata
        """
        pdf_path = Path(pdf_path)
        print(f"📄 Processing PDF query: {pdf_path.name}")
        
        # Transform PDF to text
        extracted_data = self.pdf_transformer.transform(str(pdf_path))
        
        if not extracted_data:
            print("   ❌ No text extracted from PDF")
            return []
        
        # Combine text from all pages
        combined_text = " ".join([page['text'] for page in extracted_data])
        print(f"   ✅ Extracted {len(combined_text)} characters from {len(extracted_data)} page(s)")
        
        # Extract key features for better matching
        feature_text = self.feature_extractor.extract_key_features(combined_text)
        print(f"   🔍 Feature extraction: {len(feature_text)} chars (from {len(combined_text)} raw)")
        
        # Search using feature-focused text
        results = self.retriever.search(feature_text, top_k=top_k,
                                       filter_conditions=filter_conditions)
        
        # Add query metadata (not source metadata - clients are stored as text)
        for result in results:
            result['query_type'] = 'pdf'
            result['query_file'] = pdf_path.name
            result['query_pages_extracted'] = len(extracted_data)
            # Source info comes from Qdrant payload (text-based clients have no source_file)
            result['source_type'] = result.get('payload', {}).get('source_type', 'text')
        
        print(f"   Found {len(results)} matching clients")
        return results
    
    def process_image_query(self, image_path: Union[str, Path], top_k: int = 5,
                           filter_conditions: Dict = None) -> List[Dict[str, Any]]:
        """
        Process an image file query.
        
        Steps:
        1. Transform image to text using OCR
        2. Use extracted text for retrieval
        
        Args:
            image_path: Path to image file
            top_k: Number of results to return
            filter_conditions: Optional filters for search
        
        Returns:
            List of search results with image metadata
        """
        image_path = Path(image_path)
        print(f"🖼️  Processing image query: {image_path.name}")
        
        # Transform image to text
        extracted_data = self.image_transformer.transform(str(image_path))
        
        if not extracted_data:
            print("   ❌ No text extracted from image")
            return []
        
        # Use extracted text
        text = extracted_data[0]['text']
        print(f"   ✅ Extracted {len(text)} characters from image")
        
        # Extract key features for better matching
        feature_text = self.feature_extractor.extract_key_features(text)
        print(f"   🔍 Feature extraction: {len(feature_text)} chars (from {len(text)} raw)")
        
        # Search using feature-focused text
        results = self.retriever.search(feature_text, top_k=top_k,
                                       filter_conditions=filter_conditions)
        
        # Add query metadata (not source metadata - clients are stored as text)
        for result in results:
            result['query_type'] = 'image'
            result['query_file'] = image_path.name
            # Source info comes from Qdrant payload (text-based clients have no source_file)
            result['source_type'] = result.get('payload', {}).get('source_type', 'text')
        
        print(f"   Found {len(results)} matching clients")
        return results
    
    def route(self, query: Union[str, Path], top_k: int = 5,
             filter_conditions: Dict = None) -> List[Dict[str, Any]]:
        """
        Main routing method. Automatically detects query type and processes accordingly.
        
        Args:
            query: Text string, PDF path, or image path
            top_k: Number of results to return
            filter_conditions: Optional filters for search
        
        Returns:
            List of search results
        """
        # Detect query type
        query_type = self.detect_query_type(query)
        print(f"🔀 Query type detected: {query_type.upper()}")
        
        # Route to appropriate processor
        if query_type == 'text':
            return self.process_text_query(query, top_k, filter_conditions)
        elif query_type == 'pdf':
            return self.process_pdf_query(query, top_k, filter_conditions)
        elif query_type == 'image':
            return self.process_image_query(query, top_k, filter_conditions)
        else:
            print(f"   ❌ Unknown query type: {query_type}")
            return []


# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    # Initialize router
    router = QueryRouter()
    
    print("\n" + "="*80)
    print("Example 1: Text Query")
    print("="*80)
    
    # Text query
    text_query = "Find clients with high income and good payment history"
    results = router.route(text_query, top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.4f}):")
        print(f"Client ID: {result['client_id']}")
        print(f"Text Preview: {result['text'][:200]}...")
    
    print("\n" + "="*80)
    print("Example 2: PDF Query")
    print("="*80)
    
    # PDF query
    pdf_path = "embeddings/pdf/raw/client_100021_financial_profile.pdf"
    if os.path.exists(pdf_path):
        results = router.route(pdf_path, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Score: {result['score']:.4f}):")
            print(f"Client ID: {result['client_id']}")
            print(f"Source: {result.get('source_file', 'N/A')}")
            print(f"Text Preview: {result['text'][:200]}...")
    else:
        print("PDF file not found. Skipping PDF query example.")
    
    print("\n" + "="*80)
    print("Example 3: Query with Filters")
    print("="*80)
    
    # Text query with filter
    results = router.route(
        "Find clients who defaulted",
        top_k=3,
        filter_conditions={'target': 1}
    )
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.4f}):")
        print(f"Client ID: {result['client_id']}")
        print(f"Target: {result['target']}")
