"""
Configuration settings for Decision Shadows web application
"""

# Page configuration
PAGE_CONFIG = {
    "page_title": "Decision Shadows",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {"About": "Multimodal RAG System for Pre-Decision Analysis"}
}

# Layout column proportions
LAYOUT_COLUMNS = [1.15, 2.4, 1.2]  # [sidebar, main, info_panel]

# API Configuration
API_CONFIG = {
    "base_url": "http://localhost:8000",
    "api_key": "dev-test-key-12345",
    "timeout": 30
}

# Default session state values
DEFAULT_SESSION_STATE = {
    "query_count": 0,
    "last_query": "",
    "api_status": "unknown",
    "last_analysis": None,
    "current_client_id": None,
    "current_profile": None,
    "last_similar_cases": None,
    "pdf_search_results": None,
    "last_pdf_query": None
}
