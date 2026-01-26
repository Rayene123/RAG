"""
Test Query System with LLM Understanding
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.query_router import QueryRouter

def test_with_llm():
    """Test query router with LLM understanding"""
    
    print("=" * 80)
    print("TESTING QUERY SYSTEM WITH LLM UNDERSTANDING")
    print("=" * 80)
    
    # Initialize router with LLM understanding
    router = QueryRouter(use_llm_understanding=True)
    
    test_cases = [
        {
            "query": "Find clients with low income and didn't pay the loan",
            "description": "The problematic query from before"
        },
        {
            "query": "Show me high-income clients who successfully paid back",
            "description": "Good standing with income filter"
        },
        {
            "query": "Find young married clients with stable employment",
            "description": "No payment status filter"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'=' * 80}")
        print(f"TEST {i}: {test['description']}")
        print(f"{'=' * 80}")
        print(f"\n📝 Query: '{test['query']}'")
        print(f"{'-' * 80}\n")
        
        try:
            results = router.route(test['query'], top_k=3)
            
            print(f"\n✅ Found {len(results)} results:\n")
            
            for j, result in enumerate(results, 1):
                risk_status = "DEFAULT" if result['target'] == 1 else "GOOD STANDING"
                print(f"  {j}. Client {result['client_id']}")
                print(f"     Score: {result['score']:.4f}")
                print(f"     Status: {risk_status}")
                print()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("ALL TESTS COMPLETE")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_with_llm()
