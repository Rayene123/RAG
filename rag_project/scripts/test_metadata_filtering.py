"""
Quick Test: Query System with Metadata Filtering
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.query_router import QueryRouter

def test_metadata_filtering():
    """Test queries with the new metadata filtering"""
    
    print("=" * 80)
    print("TESTING QUERY SYSTEM WITH METADATA FILTERING")
    print("=" * 80)
    
    # Initialize router with LLM understanding
    router = QueryRouter(use_llm_understanding=True)
    
    test_cases = [
        {
            "query": "Find young married female clients who didn't pay the loan",
            "description": "Multiple demographic filters + payment status"
        },
        {
            "query": "Show me clients with low income and didn't pay",
            "description": "Income range + payment status"
        },
        {
            "query": "Find clients who own real estate and paid back successfully",
            "description": "Asset ownership + good standing"
        },
        {
            "query": "Show pensioners with 2 or more children who defaulted",
            "description": "Income type + children count + payment status"
        },
        {
            "query": "Find high income male clients over 50 years old",
            "description": "Gender + age range + income range"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'=' * 80}")
        print(f"TEST {i}: {test['description']}")
        print(f"{'=' * 80}")
        print(f"\n📝 Query: '{test['query']}'")
        print(f"{'-' * 80}\n")
        
        try:
            results = router.route(test['query'], top_k=5)
            
            print(f"\n✅ Found {len(results)} results:\n")
            
            for j, result in enumerate(results, 1):
                risk_status = "DEFAULTED" if result['target'] == 1 else "PAID BACK"
                payload = result.get('payload', {})
                
                print(f"  {j}. Client {result['client_id']}")
                print(f"     Score: {result['score']:.4f}")
                print(f"     Status: {risk_status}")
                print(f"     Gender: {payload.get('CODE_GENDER', 'N/A')}")
                print(f"     Marital: {payload.get('NAME_FAMILY_STATUS', 'N/A')}")
                print(f"     Age: {-int(payload.get('DAYS_BIRTH', 0))//365 if payload.get('DAYS_BIRTH') else 'N/A'} years")
                print(f"     Income: ${payload.get('AMT_INCOME_TOTAL', 0):,.0f}")
                print(f"     Children: {payload.get('CNT_CHILDREN', 'N/A')}")
                print(f"     Owns Real Estate: {payload.get('FLAG_OWN_REALTY', 'N/A')}")
                print()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("ALL TESTS COMPLETE")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_metadata_filtering()
