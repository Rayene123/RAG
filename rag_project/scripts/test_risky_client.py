"""
Test retrieval with a high-risk client profile.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.pipeline.query_pipeline import QueryPipeline


def test_risky_profile():
    """Test with a high-risk client query"""
    print("\n" + "="*80)
    print("TESTING HIGH-RISK CLIENT RETRIEVAL")
    print("="*80)
    
    pipeline = QueryPipeline()
    
    # Create a risky text query
    risky_query = """
    Client with high debt burden, late payment history, 
    multiple overdue accounts, low payment completion ratio,
    unstable employment, high debt-to-income ratio,
    current overdue payments, previous loan rejections
    """
    
    print("\nSearching for similar risky clients...")
    print(f"Query: {risky_query.strip()}")
    
    result = pipeline.search_text(
        risky_query,
        top_k=3,
        verbose=True
    )
    
    print("\n" + "="*80)
    print("SUMMARY OF RETRIEVED CLIENTS")
    print("="*80)
    
    for i, res in enumerate(result['results'], 1):
        risk_status = "DEFAULT RISK" if res.get('target') == 1 else "GOOD STANDING"
        print(f"\n{i}. Client {res['client_id']} - Score: {res['score']:.4f}")
        print(f"   Risk Status: {risk_status}")


def test_good_standing_profile():
    """Test with a low-risk client query"""
    print("\n\n" + "="*80)
    print("TESTING LOW-RISK CLIENT RETRIEVAL (for comparison)")
    print("="*80)
    
    pipeline = QueryPipeline()
    
    # Create a low-risk text query
    good_query = """
    Client with zero outstanding debt, excellent payment completion ratio,
    100% on-time payments, no overdue history, stable long-term employment,
    low debt-to-income ratio, all previous loans approved,
    no current overdue, high income
    """
    
    print("\nSearching for similar low-risk clients...")
    print(f"Query: {good_query.strip()}")
    
    result = pipeline.search_text(
        good_query,
        top_k=3,
        verbose=True
    )
    
    print("\n" + "="*80)
    print("SUMMARY OF RETRIEVED CLIENTS")
    print("="*80)
    
    for i, res in enumerate(result['results'], 1):
        risk_status = "DEFAULT RISK" if res.get('target') == 1 else "GOOD STANDING"
        print(f"\n{i}. Client {res['client_id']} - Score: {res['score']:.4f}")
        print(f"   Risk Status: {risk_status}")


if __name__ == "__main__":
    try:
        # Test risky profile
        test_risky_profile()
        
        # Test good profile for comparison
        test_good_standing_profile()
        
        print("\n\n" + "="*80)
        print("[SUCCESS] RISK PROFILE TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
