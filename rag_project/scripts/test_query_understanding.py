"""
Test Query Understanding
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.query_understanding import QueryUnderstanding

def test_query_understanding():
    """Test query understanding with various natural language queries"""
    
    understanding = QueryUnderstanding()
    
    print("=" * 80)
    print("TESTING QUERY UNDERSTANDING")
    print("=" * 80)
    
    test_queries = [
        "Find clients with low income and didn't pay the loan",
        "Show me clients who successfully paid back their loans",
        "Find young clients who defaulted",
        "High income clients with good standing",
        "Find risky clients with stable employment",
        "Show middle-aged clients who repaid successfully",
        "Find clients who failed to pay with high income",
    ]
    
    for query in test_queries:
        print(f"\n{'-' * 80}")
        print(f"Query: '{query}'")
        print(f"{'-' * 80}")
        
        parsed = understanding.parse_query(query)
        
        print(f"\n📊 Parsed Results:")
        print(f"   Intent: {parsed['intent'] or 'None detected'}")
        print(f"   Filters: {parsed['filters'] if parsed['filters'] else 'None'}")
        print(f"   Search Query: '{parsed['search_query']}'")
        
        if parsed['detected_filters']:
            print(f"\n🏷️  Detected Filters:")
            for f in parsed['detected_filters']:
                print(f"   - {f}")

if __name__ == "__main__":
    test_query_understanding()
