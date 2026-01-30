"""
Integration Example: RAGAS Evaluation with FastAPI Endpoints.

This script shows how to evaluate your FastAPI search endpoints using RAGAS.
"""

import os
import sys
import requests
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from evaluation import RAGASEvaluator, DatasetBuilder


class APIEvaluator:
    """
    Evaluates RAG system through API endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API evaluator.
        
        Args:
            base_url: Base URL of the FastAPI server
        """
        self.base_url = base_url
        self.builder = DatasetBuilder()
    
    def check_api_health(self) -> bool:
        """Check if API is running."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def query_api(self, query: str, top_k: int = 5) -> dict:
        """
        Query the search API endpoint.
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            API response dictionary
        """
        endpoint = f"{self.base_url}/api/v1/search"
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def add_api_result_to_dataset(
        self,
        query: str,
        api_response: dict,
        ground_truth: str = None
    ):
        """
        Add API result to evaluation dataset.
        
        Args:
            query: The search query
            api_response: Response from API
            ground_truth: Optional ground truth answer
        """
        # Extract contexts from API response
        contexts = []
        results = api_response.get('results', [])
        
        for result in results:
            # Combine relevant fields into context
            context = f"Client ID: {result.get('client_id', 'N/A')}\n"
            context += f"Risk Status: {'DEFAULT RISK' if result.get('target') == 1 else 'GOOD STANDING'}\n"
            context += f"Text: {result.get('text', '')}"
            contexts.append(context)
        
        # Generate answer (in production, you'd call an LLM endpoint)
        answer = self._generate_answer_from_contexts(query, contexts)
        
        # Add to dataset
        self.builder.add_sample(
            question=query,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth
        )
    
    def _generate_answer_from_contexts(self, query: str, contexts: list) -> str:
        """Generate answer from contexts."""
        if not contexts:
            return "No relevant information found."
        
        # Simple answer generation
        return f"Based on the search results: {contexts[0][:300]}..."
    
    def evaluate_api_performance(self, test_queries: list) -> dict:
        """
        Evaluate API performance using RAGAS.
        
        Args:
            test_queries: List of test queries or dicts with 'question' and 'ground_truth'
        
        Returns:
            Evaluation results
        """
        if not self.check_api_health():
            raise RuntimeError(f"API not available at {self.base_url}")
        
        print(f"✅ API is running at {self.base_url}")
        print(f"\n📊 Evaluating {len(test_queries)} queries...\n")
        
        # Process each query
        for i, query_item in enumerate(test_queries, 1):
            if isinstance(query_item, str):
                query = query_item
                ground_truth = None
            else:
                query = query_item.get('question', query_item.get('query'))
                ground_truth = query_item.get('ground_truth')
            
            print(f"   {i}/{len(test_queries)}: {query[:60]}...")
            
            try:
                # Query API
                api_response = self.query_api(query)
                
                # Add to evaluation dataset
                self.add_api_result_to_dataset(query, api_response, ground_truth)
                
            except Exception as e:
                print(f"      ❌ Failed: {str(e)}")
                continue
        
        # Build dataset and evaluate
        dataset = self.builder.build_dataset()
        print(f"\n✅ Dataset built with {len(dataset)} samples")
        
        # Run RAGAS evaluation with Mistral
        evaluator = RAGASEvaluator(llm_provider="mistral", embeddings_model="huggingface")
        
        from evaluation import get_ragas_metrics
        has_ground_truth = 'ground_truth' in dataset.column_names
        metrics = get_ragas_metrics(include_all=has_ground_truth)
        
        print(f"\n🔍 Running RAGAS evaluation...")
        results = evaluator.evaluate_dataset(dataset, metrics=metrics)
        
        return results


def main():
    """
    Main function to run API evaluation.
    """
    print("="*80)
    print("RAGAS Evaluation - FastAPI Integration")
    print("="*80)
    
    # Initialize evaluator
    api_evaluator = APIEvaluator(base_url="http://localhost:8000")
    
    # Test queries
    test_queries = [
        "Find clients with high income and education level",
        "Show me clients who have defaulted on loans",
        "Retrieve information about clients with low credit amounts",
        {
            "question": "What factors indicate loan default risk?",
            "ground_truth": "Key default risk indicators include previous payment difficulties (TARGET=1), overdue payments, and low income relative to credit amount."
        }
    ]
    
    try:
        # Run evaluation
        results = api_evaluator.evaluate_api_performance(test_queries)
        
        print("\n" + "="*80)
        print("✅ API Evaluation Complete!")
        print("="*80)
        
        # Save results
        output_path = os.path.join(project_root, "evaluation", "api_evaluation_results.csv")
        api_evaluator.builder.save_to_csv(output_path)
        print(f"\n💾 Results saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Note: Make sure your FastAPI server is running before executing this script
    # Start server with: uvicorn api.main:app --reload
    
    main()
