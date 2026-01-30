"""
RAGAS Evaluator for RAG System.

Main evaluation class that runs RAGAS metrics on the RAG pipeline.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from datasets import Dataset

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_relevancy
)

from evaluation.metrics_config import get_ragas_metrics, get_metric_descriptions


class RAGASEvaluator:
    """
    Evaluates RAG system performance using RAGAS metrics.
    """
    
    def __init__(self, llm_provider: str = "openai", embeddings_model: str = "openai"):
        """
        Initialize RAGAS Evaluator.
        
        Args:
            llm_provider: LLM provider for evaluation ("openai", "azure", etc.)
            embeddings_model: Embeddings model for evaluation
        """
        self.llm_provider = llm_provider
        self.embeddings_model = embeddings_model
        
        print(f"✅ RAGASEvaluator initialized with {llm_provider}")
    
    def evaluate_dataset(
        self,
        dataset: Dataset,
        metrics: Optional[List] = None,
        verbose: bool = True
    ) -> Dict[str, float]:
        """
        Evaluate a dataset using RAGAS metrics.
        
        Args:
            dataset: HuggingFace Dataset with question, answer, contexts, and optionally ground_truth
            metrics: List of RAGAS metrics to use. If None, uses all available metrics.
            verbose: Whether to print progress
        
        Returns:
            Dictionary of metric scores
        """
        if metrics is None:
            # Determine if we have ground truth
            has_ground_truth = 'ground_truth' in dataset.column_names
            metrics = get_ragas_metrics(include_all=has_ground_truth)
        
        if verbose:
            print(f"\n{'='*80}")
            print("RAGAS Evaluation Started")
            print(f"{'='*80}")
            print(f"Dataset size: {len(dataset)}")
            print(f"Metrics: {[m.name for m in metrics]}")
            print(f"{'='*80}\n")
        
        # Run RAGAS evaluation
        try:
            result = evaluate(
                dataset=dataset,
                metrics=metrics,
            )
            
            if verbose:
                self._print_results(result)
            
            return result
        
        except Exception as e:
            print(f"❌ Evaluation failed: {str(e)}")
            raise
    
    def _print_results(self, result: Dict[str, float]):
        """
        Print evaluation results in a formatted way.
        
        Args:
            result: Dictionary of metric scores
        """
        print(f"\n{'='*80}")
        print("RAGAS Evaluation Results")
        print(f"{'='*80}\n")
        
        descriptions = get_metric_descriptions()
        
        for metric_name, score in result.items():
            if metric_name in descriptions:
                print(f"📊 {metric_name.upper()}")
                print(f"   Score: {score:.4f}")
                print(f"   {descriptions[metric_name]}")
                print()
    
    def evaluate_and_save(
        self,
        dataset: Dataset,
        output_path: str,
        metrics: Optional[List] = None,
        verbose: bool = True
    ) -> Dict[str, float]:
        """
        Evaluate dataset and save results to file.
        
        Args:
            dataset: Dataset to evaluate
            output_path: Path to save results (CSV or JSON)
            metrics: List of metrics to use
            verbose: Whether to print progress
        
        Returns:
            Dictionary of metric scores
        """
        result = self.evaluate_dataset(dataset, metrics, verbose)
        
        # Save results
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix == '.json':
            import json
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            # Save as CSV
            df = pd.DataFrame([result])
            df.to_csv(output_path, index=False)
        
        print(f"\n✅ Results saved to {output_path}")
        
        return result
    
    def compare_runs(
        self,
        results_list: List[Dict[str, Any]],
        labels: List[str]
    ) -> pd.DataFrame:
        """
        Compare multiple evaluation runs.
        
        Args:
            results_list: List of evaluation result dictionaries
            labels: Labels for each run
        
        Returns:
            DataFrame comparing the runs
        """
        if len(results_list) != len(labels):
            raise ValueError("results_list and labels must have the same length")
        
        comparison_data = []
        for label, result in zip(labels, results_list):
            row = {'Run': label}
            row.update(result)
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        
        print(f"\n{'='*80}")
        print("RAGAS Comparison Results")
        print(f"{'='*80}\n")
        print(df.to_string(index=False))
        
        return df
    
    def get_metric_stats(
        self,
        dataset: Dataset,
        metric_name: str
    ) -> Dict[str, float]:
        """
        Get detailed statistics for a specific metric across all samples.
        
        Args:
            dataset: Dataset to evaluate
            metric_name: Name of the metric to analyze
        
        Returns:
            Dictionary with mean, std, min, max scores
        """
        # Map metric names to metric objects
        metric_map = {
            'faithfulness': faithfulness,
            'answer_relevancy': answer_relevancy,
            'context_precision': context_precision,
            'context_recall': context_recall,
            'context_relevancy': context_relevancy
        }
        
        if metric_name not in metric_map:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        metric = metric_map[metric_name]
        result = evaluate(dataset=dataset, metrics=[metric])
        
        # Get individual scores from the dataset
        scores = result.get(metric_name, [])
        
        if isinstance(scores, (int, float)):
            # Single aggregated score
            return {
                'mean': scores,
                'std': 0.0,
                'min': scores,
                'max': scores
            }
        else:
            # Multiple scores
            import numpy as np
            return {
                'mean': np.mean(scores),
                'std': np.std(scores),
                'min': np.min(scores),
                'max': np.max(scores)
            }
