"""
Sample script to run RAGAS evaluation on the RAG system.

This script demonstrates how to:
1. Query the RAG system
2. Collect results
3. Build an evaluation dataset
4. Run RAGAS metrics
5. Analyze results
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from evaluation import RAGASEvaluator, DatasetBuilder, get_ragas_metrics
from rag_core.pipeline.query_pipeline import QueryPipeline
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI


def create_answer_from_contexts(question: str, contexts: list) -> str:
    """
    Generate an answer from retrieved contexts using an LLM.
    
    Args:
        question: The user question
        contexts: Retrieved contexts
    
    Returns:
        Generated answer
    """
    if not contexts:
        return "No relevant information found."
    
    # Use Mistral LLM to generate a proper answer
    try:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            # Fallback to simple concatenation if no API key
            return f"Based on the retrieved client information:\n\n{contexts[0][:500]}"
        
        llm = ChatMistralAI(model="mistral-large-latest", api_key=api_key)
        
        # Combine all contexts
        combined_context = "\n\n---\n\n".join(contexts[:3])  # Use top 3 contexts
        
        # Create prompt for answer generation
        prompt = f"""You are a financial analyst assistant. Answer the user's question based on the provided client information.

Question: {question}

Client Information:
{combined_context}

Instructions:
- Provide a direct, specific answer to the question
- Use information from the client profiles provided
- Be concise but complete
- If multiple clients match, mention the most relevant ones
- Include specific details like Client IDs, amounts, and risk status when relevant

Answer:"""
        
        # Generate answer
        response = llm.invoke(prompt)
        return response.content.strip()
        
    except Exception as e:
        print(f"⚠️ Error generating answer with LLM: {e}")
        # Fallback to simple concatenation
        return f"Based on the retrieved client information:\n\n{contexts[0][:500]}"


def run_basic_evaluation():
    """
    Run a basic RAGAS evaluation on sample queries.
    """
    print("="*80)
    print("RAGAS Evaluation - Basic Example")
    print("="*80)
    
    # Load environment variables (for API keys)
    load_dotenv()
    
    # Initialize RAG pipeline
    print("\n1️⃣ Initializing RAG Pipeline...")
    pipeline = QueryPipeline()
    
    # Initialize dataset builder
    print("\n2️⃣ Building Evaluation Dataset...")
    builder = DatasetBuilder()
    
    # Improved sample queries - more specific and answerable
    test_queries = [
        "What is the income and education level of client 256873?",
        "What is the risk status of clients with overdue payments?",
        "Show me the credit amount and employment details for high-income clients",
        "What is the payment completion ratio for clients with DEFAULT RISK status?",
        "Find clients who own real estate and have higher education"
    ]
    
    # Collect RAG results for each query
    for question in test_queries:
        print(f"\n   Processing: '{question}'")
        
        # Query the RAG system
        rag_results = pipeline.execute(question, top_k=3, verbose=False)
        
        # Extract contexts
        contexts = []
        for result in rag_results.get('results', []):
            contexts.append(result.get('text', ''))
        
        # Generate answer
        answer = create_answer_from_contexts(question, contexts)
        
        # Add to dataset
        builder.add_sample(
            question=question,
            answer=answer,
            contexts=contexts
        )
    
    # Build dataset
    dataset = builder.build_dataset()
    print(f"\n✅ Dataset built with {len(dataset)} samples")
    print(f"   Summary: {builder.get_summary()}")
    
    # Save dataset for future use
    dataset_path = os.path.join(project_root, "evaluation", "sample_dataset.csv")
    builder.save_to_csv(dataset_path)
    
    # Initialize RAGAS evaluator with Mistral
    print("\n3️⃣ Running RAGAS Evaluation...")
    evaluator = RAGASEvaluator(llm_provider="mistral", embeddings_model="huggingface")
    
    # Get metrics that don't require ground truth
    metrics = get_ragas_metrics(include_all=False)
    
    # Run evaluation
    results = evaluator.evaluate_dataset(
        dataset=dataset,
        metrics=metrics,
        verbose=True
    )
    
    # Save results
    results_path = os.path.join(project_root, "evaluation", "evaluation_results.csv")
    evaluator.evaluate_and_save(
        dataset=dataset,
        output_path=results_path,
        metrics=metrics,
        verbose=False
    )
    
    return results


def run_evaluation_with_ground_truth():
    """
    Run evaluation with ground truth answers for full metrics.
    """
    print("="*80)
    print("RAGAS Evaluation - With Ground Truth")
    print("="*80)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    print("\n1️⃣ Initializing Components...")
    pipeline = QueryPipeline()
    builder = DatasetBuilder()
    
    # Sample queries with ground truth
    test_cases = [
        {
            "question": "Find clients with high income and education level",
            "ground_truth": "Clients with income above 200,000 and higher education are considered financially stable and typically have good credit history."
        },
        {
            "question": "Show me clients who have defaulted on loans",
            "ground_truth": "Defaulted clients have TARGET=1 in their records, indicating payment difficulties in previous loans."
        }
    ]
    
    # Process each test case
    print("\n2️⃣ Processing Test Cases...")
    for test_case in test_cases:
        question = test_case["question"]
        ground_truth = test_case["ground_truth"]
        
        print(f"\n   Processing: '{question}'")
        
        # Query RAG system
        rag_results = pipeline.execute(question, top_k=3, verbose=False)
        
        # Extract contexts
        contexts = []
        for result in rag_results.get('results', []):
            contexts.append(result.get('text', ''))
        
        # Generate answer
        answer = create_answer_from_contexts(question, contexts)
        
        # Add with ground truth
        builder.add_sample(
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth
        )
    
    # Build dataset
    dataset = builder.build_dataset()
    print(f"\n✅ Dataset built with {len(dataset)} samples")
    
    # Run full evaluation with all metrics
    print("\n3️⃣ Running Full RAGAS Evaluation...")
    evaluator = RAGASEvaluator(llm_provider="mistral", embeddings_model="huggingface")
    
    # Use all metrics since we have ground truth
    metrics = get_ragas_metrics(include_all=True)
    
    results = evaluator.evaluate_dataset(
        dataset=dataset,
        metrics=metrics,
        verbose=True
    )
    
    return results


def compare_different_configurations():
    """
    Compare RAG system performance with different configurations.
    """
    print("="*80)
    print("RAGAS Evaluation - Configuration Comparison")
    print("="*80)
    
    # This is a template - you would run evaluations with different top_k values,
    # different embedding models, etc.
    
    # Example: Compare top_k=3 vs top_k=5
    results_list = []
    labels = []
    
    for top_k in [3, 5]:
        print(f"\n📊 Evaluating with top_k={top_k}")
        
        pipeline = QueryPipeline()
        builder = DatasetBuilder()
        
        # Sample queries
        test_queries = [
            "Find clients with defaults",
            "Show high income clients"
        ]
        
        for question in test_queries:
            rag_results = pipeline.execute(question, top_k=top_k, verbose=False)
            
            contexts = []
            for result in rag_results.get('results', []):
                contexts.append(result.get('text', ''))
            
            answer = create_answer_from_contexts(question, contexts)
            builder.add_sample(question=question, answer=answer, contexts=contexts)
        
        dataset = builder.build_dataset()
        evaluator = RAGASEvaluator(llm_provider="mistral", embeddings_model="huggingface")
        
        result = evaluator.evaluate_dataset(
            dataset=dataset,
            metrics=get_ragas_metrics(include_all=False),
            verbose=False
        )
        
        results_list.append(result)
        labels.append(f"top_k={top_k}")
    
    # Compare results
    evaluator = RAGASEvaluator()
    comparison_df = evaluator.compare_runs(results_list, labels)
    
    # Save comparison
    comparison_path = os.path.join(project_root, "evaluation", "comparison_results.csv")
    comparison_df.to_csv(comparison_path, index=False)
    print(f"\n✅ Comparison saved to {comparison_path}")
    
    return comparison_df


if __name__ == "__main__":
    print("\n🚀 Starting RAGAS Evaluation Script\n")
    
    # Run basic evaluation without ground truth
    print("\n" + "="*80)
    print("OPTION 1: Basic Evaluation (no ground truth required)")
    print("="*80)
    try:
        results = run_basic_evaluation()
        print("\n✅ Basic evaluation completed successfully!")
    except Exception as e:
        print(f"\n❌ Basic evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Uncomment to run with ground truth
    # print("\n" + "="*80)
    # print("OPTION 2: Evaluation with Ground Truth")
    # print("="*80)
    # try:
    #     results_gt = run_evaluation_with_ground_truth()
    #     print("\n✅ Ground truth evaluation completed!")
    # except Exception as e:
    #     print(f"\n❌ Ground truth evaluation failed: {str(e)}")
    
    # Uncomment to run comparison
    # print("\n" + "="*80)
    # print("OPTION 3: Configuration Comparison")
    # print("="*80)
    # try:
    #     comparison = compare_different_configurations()
    #     print("\n✅ Comparison completed!")
    # except Exception as e:
    #     print(f"\n❌ Comparison failed: {str(e)}")
    
    print("\n" + "="*80)
    print("Evaluation Complete!")
    print("="*80)
