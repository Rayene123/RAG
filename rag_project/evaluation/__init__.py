"""
RAGAS Evaluation Module for RAG System.

This module provides tools to evaluate the RAG system using RAGAS metrics:
- Faithfulness: Measures if the answer is grounded in the retrieved context
- Answer Relevancy: Measures how relevant the answer is to the question
- Context Precision: Measures if all relevant items are ranked higher
- Context Recall: Measures if all relevant info is retrieved
- Context Relevancy: Measures if retrieved contexts are relevant
"""

from .ragas_evaluator import RAGASEvaluator
from .dataset_builder import DatasetBuilder
from .metrics_config import get_ragas_metrics

__all__ = [
    'RAGASEvaluator',
    'DatasetBuilder',
    'get_ragas_metrics'
]
