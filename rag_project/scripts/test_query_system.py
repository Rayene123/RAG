"""
Test Query Router and Pipeline with different query types.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.query_router import QueryRouter
from rag_core.pipeline.query_pipeline import QueryPipeline


def test_query_router():
    """Test the Query Router with different query types"""
    print("\n" + "="*80)
    print("TESTING QUERY ROUTER")
    print("="*80)
    
    # Initialize router
    router = QueryRouter()
    
    # Test 1: Text query
    print("\n" + "-"*80)
    print("TEST 1: Text Query")
    print("-"*80)
    
    text_query = "Find clients with low income and didn't pay the loan"
    results = router.route(text_query, top_k=2)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. Client {result['client_id']} (Score: {result['score']:.4f})")
        print(f"     Risk: {'DEFAULT' if result['target'] == 1 else 'GOOD STANDING'}")
    
    # Test 2: PDF query
    print("\n" + "-"*80)
    print("TEST 2: PDF Query")
    print("-"*80)
    
    pdf_path = project_root / "embeddings" / "pdf" / "raw" / "client_100021_financial_profile.pdf"
    if pdf_path.exists():
        results = router.route(str(pdf_path), top_k=2)
        
        print(f"\nFound {len(results)} similar clients:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. Client {result['client_id']} (Score: {result['score']:.4f})")
            print(f"     Source: {result.get('source_file', 'N/A')}")
            print(f"     Risk: {'DEFAULT' if result['target'] == 1 else 'GOOD STANDING'}")
    else:
        print("PDF file not found. Skipping test.")
    
    # Test 3: Query type detection
    print("\n" + "-"*80)
    print("TEST 3: Query Type Detection")
    print("-"*80)
    
    test_cases = [
        "This is a text query",
        "embeddings/pdf/raw/client_100021_financial_profile.pdf",
        "embeddings/image/raw/sample.png",
    ]
    
    for test in test_cases:
        query_type = router.detect_query_type(test)
        print(f"  '{test}' -> {query_type.upper()}")


def test_query_pipeline():
    """Test the Query Pipeline"""
    print("\n\n" + "="*80)
    print("TESTING QUERY PIPELINE")
    print("="*80)
    
    # Initialize pipeline
    pipeline = QueryPipeline()
    
    # Test 1: Text search
    print("\n" + "-"*80)
    print("TEST 1: Text Search with Pipeline")
    print("-"*80)
    
    result = pipeline.search_text(
        "Find young married clients with children and good payment history",
        top_k=2,
        verbose=False
    )
    
    print(f"\nQuery Type: {result['query_type']}")
    print(f"Results Found: {result['num_results']}")
    
    for i, res in enumerate(result['results'], 1):
        print(f"\n  Result {i}:")
        print(f"    Client ID: {res['client_id']}")
        print(f"    Score: {res['score']:.4f}")
    
    # Test 2: PDF search
    print("\n" + "-"*80)
    print("TEST 2: PDF Search with Pipeline")
    print("-"*80)
    
    pdf_path = project_root / "embeddings" / "pdf" / "raw" / "client_100030_financial_profile.pdf"
    if pdf_path.exists():
        result = pipeline.search_pdf(str(pdf_path), top_k=2, verbose=False)
        
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Results Found: {result['num_results']}")
        
        for i, res in enumerate(result['results'], 1):
            print(f"\n  Result {i}:")
            print(f"    Client ID: {res['client_id']}")
            print(f"    Score: {res['score']:.4f}")
            print(f"    Source: {res.get('source_file', 'N/A')}")
    else:
        print("PDF file not found. Skipping test.")
    
    # Test 3: Filtered search
    print("\n" + "-"*80)
    print("TEST 3: Filtered Search (Good Standing Only)")
    print("-"*80)
    
    result = pipeline.search_with_filter(
        "Find clients with stable employment",
        target=0,  # Only good standing
        top_k=2,
        verbose=False
    )
    
    print(f"\nFilter Applied: target=0 (Good Standing)")
    print(f"Results Found: {result['num_results']}")
    
    for i, res in enumerate(result['results'], 1):
        print(f"\n  Result {i}:")
        print(f"    Client ID: {res['client_id']}")
        print(f"    Score: {res['score']:.4f}")
        print(f"    Target: {res['target']} (GOOD STANDING)")


def test_full_pipeline_verbose():
    """Test full pipeline with verbose output"""
    print("\n\n" + "="*80)
    print("FULL PIPELINE TEST WITH VERBOSE OUTPUT")
    print("="*80)
    
    pipeline = QueryPipeline()
    
    # Test with PDF
    pdf_path = project_root / "embeddings" / "pdf" / "raw" / "client_100033_financial_profile.pdf"
    if pdf_path.exists():
        print("\nSearching for similar clients based on PDF profile...")
        result = pipeline.search_pdf(str(pdf_path), top_k=2, verbose=True)
    else:
        print("\nSearching for clients with text query...")
        result = pipeline.search_text(
            "Find clients with married status, owns real estate, and high payment completion",
            top_k=2,
            verbose=True
        )


def main():
    """Run all tests"""
    print("\n" + "QUERY ROUTER & PIPELINE TEST SUITE")
    print("="*80)
    
    try:
        # Test router
        test_query_router()
        
        # Test pipeline
        test_query_pipeline()
        
        # Test full pipeline with verbose
        test_full_pipeline_verbose()
        
        print("\n\n" + "="*80)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\n\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
