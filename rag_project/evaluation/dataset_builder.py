"""
Dataset Builder for RAGAS Evaluation.

Prepares datasets in the format required by RAGAS:
- question: The user query
- answer: Generated answer from RAG system
- contexts: Retrieved documents/contexts
- ground_truth: Expected answer (optional, for some metrics)
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


class DatasetBuilder:
    """
    Builds datasets for RAGAS evaluation from RAG system outputs.
    """
    
    def __init__(self):
        """Initialize DatasetBuilder."""
        self.data = []
    
    def add_sample(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None
    ):
        """
        Add a single evaluation sample.
        
        Args:
            question: The user query/question
            answer: Generated answer from the RAG system
            contexts: List of retrieved context strings
            ground_truth: Expected correct answer (optional)
        """
        sample = {
            'question': question,
            'answer': answer,
            'contexts': contexts,
        }
        
        if ground_truth:
            sample['ground_truth'] = ground_truth
        
        self.data.append(sample)
    
    def add_from_rag_results(
        self,
        question: str,
        rag_results: Dict[str, Any],
        answer_generator=None,
        ground_truth: Optional[str] = None
    ):
        """
        Add sample from RAG pipeline results.
        
        Args:
            question: The user query
            rag_results: Results from QueryPipeline.execute()
            answer_generator: Optional function to generate answer from contexts
            ground_truth: Expected correct answer (optional)
        """
        # Extract contexts from RAG results
        contexts = []
        results = rag_results.get('results', [])
        
        for result in results:
            # Get the text content from each result
            text = result.get('text', '')
            if text:
                contexts.append(text)
        
        # Generate or use provided answer
        if answer_generator and contexts:
            answer = answer_generator(question, contexts)
        else:
            # Default: concatenate top contexts as "answer"
            answer = self._create_default_answer(question, contexts)
        
        self.add_sample(
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth
        )
    
    def _create_default_answer(self, question: str, contexts: List[str]) -> str:
        """
        Create a default answer from contexts.
        
        Args:
            question: The question
            contexts: Retrieved contexts
        
        Returns:
            Generated answer
        """
        if not contexts:
            return "No relevant information found."
        
        # Simple answer: return most relevant context excerpt
        return f"Based on the retrieved information: {contexts[0][:500]}..."
    
    def build_dataset(self) -> Dataset:
        """
        Build HuggingFace Dataset for RAGAS evaluation.
        
        Returns:
            Dataset object ready for RAGAS
        """
        if not self.data:
            raise ValueError("No samples added. Use add_sample() or add_from_rag_results() first.")
        
        return Dataset.from_list(self.data)
    
    def save_to_csv(self, filepath: str):
        """
        Save dataset to CSV file.
        
        Args:
            filepath: Path to save CSV
        """
        df = pd.DataFrame(self.data)
        df.to_csv(filepath, index=False)
        print(f"✅ Dataset saved to {filepath}")
    
    def load_from_csv(self, filepath: str):
        """
        Load dataset from CSV file.
        
        Args:
            filepath: Path to CSV file
        """
        df = pd.read_csv(filepath)
        
        # Convert contexts from string to list if needed
        for idx, row in df.iterrows():
            sample = {
                'question': row['question'],
                'answer': row['answer'],
                'contexts': eval(row['contexts']) if isinstance(row['contexts'], str) else row['contexts']
            }
            
            if 'ground_truth' in row and pd.notna(row['ground_truth']):
                sample['ground_truth'] = row['ground_truth']
            
            self.data.append(sample)
        
        print(f"✅ Loaded {len(self.data)} samples from {filepath}")
    
    def clear(self):
        """Clear all samples."""
        self.data = []
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the dataset.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.data:
            return {"total_samples": 0}
        
        return {
            "total_samples": len(self.data),
            "has_ground_truth": sum(1 for s in self.data if 'ground_truth' in s),
            "avg_contexts_per_sample": sum(len(s['contexts']) for s in self.data) / len(self.data),
            "avg_answer_length": sum(len(s['answer']) for s in self.data) / len(self.data)
        }
