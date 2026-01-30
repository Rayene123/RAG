"""
Debug: Voir quels clients sont retournés pour différentes requêtes
"""
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from rag_core.retriever.qdrant_retriever import QdrantRetriever
import re

def extract_income(text):
    match = re.search(r'(?:annual\s+)?income[:\s]+\$?([\d,]+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return "N/A"

def extract_credit(text):
    match = re.search(r'(?:requested\s+)?credit(?:\s+amount)?[:\s]+\$?([\d,]+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return "N/A"

retriever = QdrantRetriever()

queries = [
    "35-year-old client, mid-level job, $60k income, owns car, requesting $150k loan",
    "35-year-old tech worker, $90k income, owns car, requesting $150k loan"
]

for i, query in enumerate(queries, 1):
    print(f"\n{'='*80}")
    print(f"QUERY {i}: {query}")
    print('='*80)
    
    results = retriever.search(query, top_k=5)
    
    for j, result in enumerate(results, 1):
        client_id = result.get('client_id')
        score = result.get('score', 0)
        text = result.get('text', '')
        
        income = extract_income(text)
        credit = extract_credit(text)
        
        print(f"\n  {j}. Client {client_id}")
        print(f"     Score: {score:.4f}")
        print(f"     Income: ${income}")
        print(f"     Credit: ${credit}")
