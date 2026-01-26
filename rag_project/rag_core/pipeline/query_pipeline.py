"""
Query Pipeline for RAG System.

End-to-end pipeline that:
1. Routes query based on type (text/PDF/image)
2. Retrieves relevant documents
3. Formats and presents results
"""

import os
import sys
from pathlib import Path
from typing import Union, List, Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from rag_core.query_processor.query_router import QueryRouter
from rag_core.retriever.qdrant_retriever import QdrantRetriever


class QueryPipeline:
    """
    End-to-end query pipeline for RAG system.
    """
    
    def __init__(self, retriever: QdrantRetriever = None):
        """
        Initialize Query Pipeline.
        
        Args:
            retriever: QdrantRetriever instance. If None, creates a new one.
        """
        # Initialize retriever
        self.retriever = retriever if retriever else QdrantRetriever()
        
        # Initialize router
        self.router = QueryRouter(retriever=self.retriever)
        
        print("✅ QueryPipeline initialized")
    
    def format_result(self, result: Dict[str, Any], rank: int) -> str:
        """
        Format a single search result for display.
        
        Args:
            result: Search result dictionary
            rank: Result rank (1-based)
        
        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"\n{'='*80}")
        lines.append(f"Result #{rank} | Score: {result['score']:.4f}")
        lines.append(f"{'='*80}")
        
        # Client info
        lines.append(f"Client ID: {result['client_id']}")
        
        # Risk status
        risk_status = "DEFAULT RISK" if result.get('target') == 1 else "GOOD STANDING"
        lines.append(f"Risk Status: {risk_status}")
        
        # Source info (where the client data came from in Qdrant)
        source_type = result.get('source_type', 'text')
        lines.append(f"Source Type: {source_type.upper()}")
        
        # Query info (if query was from PDF/image)
        if 'query_type' in result:
            lines.append(f"Query Type: {result['query_type'].upper()}")
            if 'query_file' in result:
                lines.append(f"Query File: {result['query_file']}")
            if 'query_pages_extracted' in result:
                lines.append(f"Pages Extracted: {result['query_pages_extracted']}")
        
        lines.append(f"\n{'-'*80}")
        lines.append("Client Profile:")
        lines.append(f"{'-'*80}")
        
        # Show full text or preview
        text = result['text']
        if len(text) > 1500:
            lines.append(text[:1500] + "\n... (truncated)")
        else:
            lines.append(text)
        
        return "\n".join(lines)
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format all search results for display.
        
        Args:
            results: List of search result dictionaries
        
        Returns:
            Formatted string
        """
        if not results:
            return "\n❌ No results found."
        
        formatted = []
        formatted.append(f"\n{'='*80}")
        formatted.append(f"SEARCH RESULTS | Found {len(results)} match(es)")
        formatted.append(f"{'='*80}")
        
        for i, result in enumerate(results, 1):
            formatted.append(self.format_result(result, i))
        
        return "\n".join(formatted)
    
    def execute(self, query: Union[str, Path], top_k: int = 5,
               filter_conditions: Dict = None, verbose: bool = True) -> Dict[str, Any]:
        """
        Execute the full query pipeline.
        
        Args:
            query: Text string, PDF path, or image path
            top_k: Number of results to return
            filter_conditions: Optional filters for search
            verbose: Whether to print formatted results
        
        Returns:
            Dictionary containing:
                - query: Original query
                - query_type: Detected query type
                - results: List of search results
                - formatted_output: Formatted string (if verbose=True)
        """
        print("\n" + "🚀 STARTING QUERY PIPELINE")
        print("="*80)
        
        # Route and retrieve
        results = self.router.route(query, top_k=top_k, 
                                   filter_conditions=filter_conditions)
        
        # Prepare output
        output = {
            'query': str(query),
            'query_type': self.router.detect_query_type(query),
            'results': results,
            'num_results': len(results)
        }
        
        # Format and display if verbose
        if verbose:
            formatted = self.format_results(results)
            output['formatted_output'] = formatted
            print(formatted)
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE")
        print("="*80)
        
        return output
    
    def search_text(self, query: str, top_k: int = 5, verbose: bool = True) -> Dict[str, Any]:
        """
        Convenience method for text queries.
        
        Args:
            query: Natural language query
            top_k: Number of results
            verbose: Whether to print results
        
        Returns:
            Pipeline output dictionary
        """
        return self.execute(query, top_k=top_k, verbose=verbose)
    
    def search_pdf(self, pdf_path: Union[str, Path], top_k: int = 5, 
                  verbose: bool = True) -> Dict[str, Any]:
        """
        Convenience method for PDF queries.
        
        Args:
            pdf_path: Path to PDF file
            top_k: Number of results
            verbose: Whether to print results
        
        Returns:
            Pipeline output dictionary
        """
        return self.execute(pdf_path, top_k=top_k, verbose=verbose)
    
    def search_image(self, image_path: Union[str, Path], top_k: int = 5,
                    verbose: bool = True) -> Dict[str, Any]:
        """
        Convenience method for image queries.
        
        Args:
            image_path: Path to image file
            top_k: Number of results
            verbose: Whether to print results
        
        Returns:
            Pipeline output dictionary
        """
        return self.execute(image_path, top_k=top_k, verbose=verbose)
    
    def search_with_filter(self, query: Union[str, Path], 
                          target: int = None, top_k: int = 5,
                          verbose: bool = True) -> Dict[str, Any]:
        """
        Convenience method for filtered queries.
        
        Args:
            query: Text string or file path
            target: Filter by target (0=good standing, 1=default risk)
            top_k: Number of results
            verbose: Whether to print results
        
        Returns:
            Pipeline output dictionary
        """
        filter_conditions = None
        if target is not None:
            filter_conditions = {'target': target}
        
        return self.execute(query, top_k=top_k, 
                          filter_conditions=filter_conditions, verbose=verbose)


# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = QueryPipeline()
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Text Query")
    print("="*80)
    
    # Execute text query
    result = pipeline.search_text(
        "Find clients with high income, stable employment, and excellent payment history",
        top_k=2
    )
    
    print("\n" + "="*80)
    print("EXAMPLE 2: PDF Query")
    print("="*80)
    
    # Execute PDF query
    pdf_path = "embeddings/pdf/raw/client_100021_financial_profile.pdf"
    if os.path.exists(pdf_path):
        result = pipeline.search_pdf(pdf_path, top_k=2)
    else:
        print("PDF file not found. Skipping PDF example.")
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Filtered Query")
    print("="*80)
    
    # Execute filtered query
    result = pipeline.search_with_filter(
        "Find clients with previous loan rejections",
        target=1,  # Filter for default risk
        top_k=2
    )
    
    print("\n" + "="*80)
    print("EXAMPLE 4: Access Results Programmatically")
    print("="*80)
    
    # Execute without verbose output
    result = pipeline.search_text(
        "Young clients with families",
        top_k=3,
        verbose=False
    )
    
    print(f"\nQuery: {result['query']}")
    print(f"Query Type: {result['query_type']}")
    print(f"Number of Results: {result['num_results']}")
    
    for i, res in enumerate(result['results'], 1):
        print(f"\n  Result {i}:")
        print(f"    Client ID: {res['client_id']}")
        print(f"    Score: {res['score']:.4f}")
        print(f"    Risk: {'DEFAULT' if res['target'] == 1 else 'GOOD'}")
