"""
Test accurate search using metadata filtering vs pure semantic search
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_core.query_processor.query_router import QueryRouter
from rag_core.retriever.qdrant_retriever import QdrantRetriever

print("="*80)
print("COMPARISON: Semantic Search vs Metadata Filtering")
print("="*80)

# Initialize both
router = QueryRouter(use_llm_understanding=True)
retriever = QdrantRetriever()

# Test Case 1: High income + owns property
print("\n" + "="*80)
print("Test 1: 'High income clients who own property'")
print("="*80)

print("\n❌ OLD WAY (Pure Semantic Search):")
semantic_results = retriever.search(
    "Find clients with high income who own property", 
    top_k=3
)
for i, r in enumerate(semantic_results, 1):
    print(f"\n  Result {i}:")
    print(f"    Age: {(-r['payload']['DAYS_BIRTH']//365)} years")
    print(f"    Income: ${r['payload']['AMT_INCOME_TOTAL']:,.0f}")
    print(f"    Owns Property: {r['payload']['FLAG_OWN_REALTY']}")
    print(f"    Score: {r['score']:.4f}")

print("\n✅ NEW WAY (Metadata Filtering):")
filtered_results = router.route(
    "Find clients with high income who own property",
    top_k=3
)
for i, r in enumerate(filtered_results, 1):
    print(f"\n  Result {i}:")
    print(f"    Age: {(-r['payload']['DAYS_BIRTH']//365)} years")
    print(f"    Income: ${r['payload']['AMT_INCOME_TOTAL']:,.0f}")
    print(f"    Owns Property: {r['payload']['FLAG_OWN_REALTY']}")
    print(f"    Score: {r['score']:.4f}")


# Test Case 2: Specific age + income range
print("\n" + "="*80)
print("Test 2: '35 year old with $50,000 income'")
print("="*80)

print("\n❌ OLD WAY (Pure Semantic Search):")
semantic_results = retriever.search_by_client_profile(
    age=35,
    income=50000,
    education="Higher education",
    top_k=3
)
for i, r in enumerate(semantic_results, 1):
    print(f"\n  Result {i}:")
    print(f"    Age: {(-r['payload']['DAYS_BIRTH']//365)} years (wanted: 35)")
    print(f"    Income: ${r['payload']['AMT_INCOME_TOTAL']:,.0f} (wanted: $50,000)")
    print(f"    Education: {r['payload']['NAME_EDUCATION_TYPE']}")
    print(f"    Score: {r['score']:.4f}")

print("\n✅ NEW WAY (Metadata Filtering):")
filtered_results = router.route(
    "Find 35 year old clients with $50,000 income and higher education",
    top_k=3
)
for i, r in enumerate(filtered_results, 1):
    print(f"\n  Result {i}:")
    print(f"    Age: {(-r['payload']['DAYS_BIRTH']//365)} years (wanted: 35)")
    print(f"    Income: ${r['payload']['AMT_INCOME_TOTAL']:,.0f} (wanted: $50,000)")
    print(f"    Education: {r['payload']['NAME_EDUCATION_TYPE']}")
    print(f"    Score: {r['score']:.4f}")


# Test Case 3: Didn't pay + married + female
print("\n" + "="*80)
print("Test 3: 'Married women who didn't pay the loan'")
print("="*80)

print("\n❌ OLD WAY (Pure Semantic Search):")
semantic_results = retriever.search(
    "married women who didn't pay the loan",
    top_k=3
)
for i, r in enumerate(semantic_results, 1):
    print(f"\n  Result {i}:")
    print(f"    Gender: {r['payload']['CODE_GENDER']}")
    print(f"    Marital: {r['payload']['NAME_FAMILY_STATUS']}")
    print(f"    Target: {'DEFAULT' if r['target'] == 1 else 'PAID'}")
    print(f"    Score: {r['score']:.4f}")

print("\n✅ NEW WAY (Metadata Filtering):")
filtered_results = router.route(
    "married women who didn't pay the loan",
    top_k=3
)
for i, r in enumerate(filtered_results, 1):
    print(f"\n  Result {i}:")
    print(f"    Gender: {r['payload']['CODE_GENDER']}")
    print(f"    Marital: {r['payload']['NAME_FAMILY_STATUS']}")
    print(f"    Target: {'DEFAULT' if r['target'] == 1 else 'PAID'}")
    print(f"    Score: {r['score']:.4f}")

print("\n" + "="*80)
print("SUMMARY:")
print("="*80)
print("❌ search() = semantic similarity only (inaccurate)")
print("✅ router.route() = LLM extracts filters + semantic search (accurate)")
print("="*80)
