"""
Decision Shadows - Main Application Entry Point
Multimodal RAG System for Pre-Decision Analysis
"""
import streamlit as st

from config import PAGE_CONFIG, LAYOUT_COLUMNS, DEFAULT_SESSION_STATE
from styles import CSS_STYLES
from components.sidebar import render_left_sidebar
from components.main_content import render_main_content
from components.info_panel import render_info_panel


def initialize_session_state():
    """Initialize session state variables"""
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header():
    """Render application header"""
    st.markdown("""
    <div class="header-container">
        <h1>⚖️ Decision Shadows</h1>
        <p>Multimodal RAG System for Pre-Decision Analysis | Financial Risk & Compliance</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Configure page
    st.set_page_config(**PAGE_CONFIG)
    
    # Apply custom styles
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Main Layout - 3 Columns
    col_sidebar, col_main, col_info = st.columns(LAYOUT_COLUMNS)
    
    # Left Sidebar - Client Profile & Decision Inputs
    with col_sidebar:
        client_profile, settings, advanced = render_left_sidebar()
    
    # Main Content Area - Shadow Generation & Analysis
    with col_main:
        render_main_content(settings["num_similar_cases"], client_profile)
    
    # Right Sidebar - Risk & Bias Analysis
    with col_info:
        render_info_panel()


if __name__ == "__main__":
    main()
