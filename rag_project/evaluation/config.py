"""
RAGAS Evaluation Configuration.

Customize evaluation settings here.
"""

# API Configuration
OPENAI_API_KEY = None  # Set in .env file
MISTRAL_API_KEY = None  # Set in .env file

# LLM Provider for RAGAS evaluation
# Options: "openai", "azure_openai", "mistral", "anthropic"
LLM_PROVIDER = "mistral"  # Using Mistral as default

# Embeddings Model for RAGAS
# Options: "openai", "huggingface"
EMBEDDINGS_PROVIDER = "huggingface"  # Using HuggingFace to avoid OpenAI dependency

# Evaluation Settings
DEFAULT_TOP_K = 5  # Number of contexts to retrieve
DEFAULT_METRICS = [
    "faithfulness",
    "answer_relevancy", 
    "context_relevancy"
]  # Metrics to use by default (without ground truth)

FULL_METRICS = [
    "faithfulness",
    "answer_relevancy",
    "context_relevancy",
    "context_precision",
    "context_recall"
]  # All metrics (requires ground truth)

# Score Thresholds
SCORE_THRESHOLDS = {
    "faithfulness": {
        "excellent": 0.9,
        "good": 0.8,
        "fair": 0.6
    },
    "answer_relevancy": {
        "excellent": 0.85,
        "good": 0.7,
        "fair": 0.5
    },
    "context_relevancy": {
        "excellent": 0.8,
        "good": 0.6,
        "fair": 0.4
    },
    "context_precision": {
        "excellent": 0.8,
        "good": 0.7,
        "fair": 0.5
    },
    "context_recall": {
        "excellent": 0.8,
        "good": 0.7,
        "fair": 0.5
    }
}

# Output Settings
SAVE_INDIVIDUAL_SCORES = True  # Save per-sample scores
SAVE_SUMMARY_STATS = True  # Save aggregated statistics
OUTPUT_FORMAT = "csv"  # Options: "csv", "json"

# Evaluation Dataset Settings
MIN_SAMPLES_FOR_EVALUATION = 1
MAX_SAMPLES_PER_BATCH = 100  # Process in batches if more samples

# FastAPI Evaluation Settings
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30  # seconds

# Paths
EVALUATION_OUTPUT_DIR = "evaluation"
RESULTS_FILENAME = "evaluation_results.csv"
DATASET_FILENAME = "test_dataset.csv"

# Test Query Categories
QUERY_CATEGORIES = [
    "profile_search",
    "risk_assessment", 
    "history_search",
    "analysis"
]

# Verbose Settings
VERBOSE_EVALUATION = True
SHOW_PROGRESS_BAR = True
PRINT_INDIVIDUAL_SCORES = False


def get_evaluation_config():
    """
    Get evaluation configuration as dictionary.
    
    Returns:
        Dictionary with all configuration settings
    """
    return {
        "llm_provider": LLM_PROVIDER,
        "embeddings_provider": EMBEDDINGS_PROVIDER,
        "default_top_k": DEFAULT_TOP_K,
        "default_metrics": DEFAULT_METRICS,
        "score_thresholds": SCORE_THRESHOLDS,
        "output_format": OUTPUT_FORMAT,
        "api_base_url": API_BASE_URL,
        "evaluation_output_dir": EVALUATION_OUTPUT_DIR
    }


def get_metric_threshold(metric_name: str, level: str = "good") -> float:
    """
    Get threshold for a specific metric.
    
    Args:
        metric_name: Name of the metric
        level: Threshold level ("excellent", "good", or "fair")
    
    Returns:
        Threshold value
    """
    return SCORE_THRESHOLDS.get(metric_name, {}).get(level, 0.5)


def is_score_acceptable(metric_name: str, score: float, level: str = "good") -> bool:
    """
    Check if a score meets the threshold.
    
    Args:
        metric_name: Name of the metric
        score: Score value
        level: Threshold level to check against
    
    Returns:
        True if score meets threshold
    """
    threshold = get_metric_threshold(metric_name, level)
    return score >= threshold


def get_score_rating(metric_name: str, score: float) -> str:
    """
    Get rating for a score.
    
    Args:
        metric_name: Name of the metric
        score: Score value
    
    Returns:
        Rating ("excellent", "good", "fair", or "poor")
    """
    thresholds = SCORE_THRESHOLDS.get(metric_name, {})
    
    if score >= thresholds.get("excellent", 1.0):
        return "excellent"
    elif score >= thresholds.get("good", 0.8):
        return "good"
    elif score >= thresholds.get("fair", 0.6):
        return "fair"
    else:
        return "poor"
