"""
Complete RAG Pipeline Demo
Shows how Query Understanding → Query Router → Retriever work together
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.query_router import QueryRouter
from rag_core.pipeline.query_pipeline import QueryPipeline

def demo_full_pipeline():
    """Demonstrate the complete RAG pipeline"""
    
    print("=" * 80)
    print("COMPLETE RAG PIPELINE DEMONSTRATION")
    print("=" * 80)
    print("\nPipeline Flow:")
    print("1. User Query (natural language)")
    print("2. Query Understanding (LLM extracts intent + filters)")
    print("3. Query Router (routes to correct handler)")
    print("4. Retriever (searches with filters + semantic search)")
    print("5. Results (formatted output)")
    print("=" * 80)
    
    # Option 1: Direct Router Usage (more control)
    print("\n\n" + "=" * 80)
    print("OPTION 1: Using Query Router Directly")
    print("=" * 80)
    
    router = QueryRouter(use_llm_understanding=True)  # LLM enabled by default
    
    query = "Find young married female clients who didn't pay the loan"
    print(f"\n📝 User Query: '{query}'")
    print("-" * 80)
    
    # The router automatically:
    # 1. Detects query type (text/pdf/image)
    # 2. Calls LLM to understand intent and extract filters
    # 3. Applies filters to Qdrant
    # 4. Returns results
    results = router.route(query, top_k=3)
    
    print(f"\n✅ Results ({len(results)} found):\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. Client {result['client_id']} (Score: {result['score']:.4f})")
        print(f"   Status: {'DEFAULTED' if result['target'] == 1 else 'PAID BACK'}")
        print(f"   Gender: {result['payload'].get('CODE_GENDER', 'N/A')}")
        print(f"   Marital: {result['payload'].get('NAME_FAMILY_STATUS', 'N/A')}")
        print(f"   Age: {-result['payload'].get('DAYS_BIRTH', 0)//365} years")
        print()
    
    # Option 2: Using Query Pipeline (cleaner interface)
    print("\n\n" + "=" * 80)
    print("OPTION 2: Using Query Pipeline (Recommended)")
    print("=" * 80)
    
    pipeline = QueryPipeline()
    
    query2 = "Show high income clients who own real estate and paid back"
    print(f"\n📝 User Query: '{query2}'")
    print("-" * 80)
    
    # Pipeline provides formatted output
    result = pipeline.search_text(query2, top_k=3, verbose=True)
    
    # Option 3: PDF Query
    print("\n\n" + "=" * 80)
    print("OPTION 3: PDF Query (with Feature Extraction)")
    print("=" * 80)
    
    pdf_path = project_root / "embeddings" / "pdf" / "raw" / "client_100033_financial_profile.pdf"
    if pdf_path.exists():
        print(f"\n📄 PDF Query: {pdf_path.name}")
        print("-" * 80)
        
        # Router handles PDF extraction + feature extraction + search
        results = router.route(str(pdf_path), top_k=3)
        
        print(f"\n✅ Found {len(results)} similar clients\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Client {result['client_id']} (Score: {result['score']:.4f})")
            print(f"   Status: {'DEFAULTED' if result['target'] == 1 else 'PAID BACK'}")
    
    # Option 4: Manual Filter Override
    print("\n\n" + "=" * 80)
    print("OPTION 4: Manual Filter Override (Advanced)")
    print("=" * 80)
    
    query3 = "Find clients with high income"
    manual_filters = {
        "target": 1,  # Force defaulted clients
        "CODE_GENDER": "F"  # Force female
    }
    
    print(f"\n📝 Query: '{query3}'")
    print(f"🔧 Manual Filters: {manual_filters}")
    print("-" * 80)
    
    # LLM understanding can be disabled, use manual filters
    router_no_llm = QueryRouter(use_llm_understanding=False)
    results = router_no_llm.process_text_query(
        query3, 
        top_k=3, 
        filter_conditions=manual_filters,
        enable_query_understanding=False
    )
    
    print(f"\n✅ Results with manual filters:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. Client {result['client_id']} (Score: {result['score']:.4f})")
        print(f"   Gender: {result['payload'].get('CODE_GENDER')}")
        print(f"   Status: {'DEFAULTED' if result['target'] == 1 else 'PAID BACK'}")
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
✅ Query Router: One-line usage, handles everything
   router.route("your query here", top_k=5)

✅ Automatic LLM Understanding: Extracts filters from natural language
   "young married female" → filters: gender=F, married, age<35

✅ Multi-modal Support: Text queries, PDF uploads, images
   Works the same for all input types

✅ Feature Extraction: PDFs get enhanced with weighted features
   Credit metrics emphasized over demographics

✅ Flexible: Can disable LLM, use manual filters, combine both
    """)

if __name__ == "__main__":
    demo_full_pipeline()
