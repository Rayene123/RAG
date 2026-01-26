"""
Test LLM-based Query Understanding
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.llm_query_understanding import LLMQueryUnderstanding

def test_llm_understanding():
    """Test LLM-based query understanding"""
    
    print("=" * 80)
    print("TESTING LLM-BASED QUERY UNDERSTANDING")
    print("=" * 80)
    
    try:
        understanding = LLMQueryUnderstanding(llm_provider="mistral")
    except Exception as e:
        print(f"\n❌ Failed to initialize LLM: {e}")
        print("\nMake sure you have:")
        print("1. Set MISTRAL_API_KEY in environment")
        print("2. Installed langchain-mistralai: pip install langchain-mistralai")
        return
    
    test_queries = [
        "Find clients with low income and didn't pay the loan",
        "Show me clients who successfully paid back their loans",
        "Find young clients who defaulted",
        "High income clients with good standing",
        "Find risky clients with stable employment",
        "Show middle-aged clients who repaid successfully",
        "Find clients who failed to pay with high income",
        "Show me clients with stable employment and owns real estate",
        "Find elderly clients with low income who defaulted",
        "Show successful young professionals who paid back",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"{'=' * 80}")
        print(f"\n📝 Query: '{query}'")
        print(f"{'-' * 80}")
        
        try:
            parsed = understanding.parse_query(query)
            
            print(f"\n📊 LLM Response:")
            print(f"   Intent: {parsed['intent'] or 'None'}")
            print(f"   Target Filter: {parsed['filters'].get('target', 'None')}")
            print(f"   Search Query: '{parsed['search_query']}'")
            
            if parsed.get('explanation'):
                print(f"\n💡 Explanation: {parsed['explanation']}")
            
            if parsed['detected_filters']:
                print(f"\n🏷️  Detected Filters:")
                for f in parsed['detected_filters']:
                    print(f"   - {f}")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n{'=' * 80}")
    print("TESTING COMPLETE")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_llm_understanding()
