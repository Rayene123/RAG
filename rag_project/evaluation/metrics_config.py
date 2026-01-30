"""
RAGAS Metrics Configuration.

Defines which metrics to use and their configuration.
"""

# Import metrics with fallback for different RAGAS versions
try:
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        context_relevancy
    )
except ImportError:
    # Try alternative import (older RAGAS versions)
    try:
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        )
        from ragas.metrics import context_relevance as context_relevancy
    except ImportError:
        # If context_relevance doesn't exist either, create a None placeholder
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        )
        context_relevancy = None


def get_ragas_metrics(include_all=True):
    """
    Get RAGAS metrics for evaluation.
    
    Args:
        include_all: If True, returns all metrics. If False, returns core metrics only.
    
    Returns:
        List of RAGAS metric instances
    """
    if include_all:
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]
        if context_relevancy is not None:
            metrics.append(context_relevancy)
        return metrics
    else:
        # Core metrics that work without ground truth
        metrics = [
            faithfulness,
            answer_relevancy,
        ]
        if context_relevancy is not None:
            metrics.append(context_relevancy)
        return metrics


def get_metric_descriptions():
    """
    Get descriptions for each metric.
    
    Returns:
        Dictionary mapping metric names to their descriptions
    """
    return {
        'faithfulness': 'Measures if the generated answer is factually consistent with the retrieved context. Score range: 0-1 (higher is better)',
        'answer_relevancy': 'Measures how relevant and to-the-point the answer is to the question. Score range: 0-1 (higher is better)',
        'context_precision': 'Measures if all the relevant items are ranked higher than irrelevant ones. Score range: 0-1 (higher is better)',
        'context_recall': 'Measures how much of the ground truth answer is covered by the retrieved context. Score range: 0-1 (higher is better)',
        'context_relevancy': 'Measures what proportion of the retrieved context is relevant to the question. Score range: 0-1 (higher is better)'
    }
