"""
Right Sidebar Components - Risk Assessment & Documentation
"""
import streamlit as st
from api_client import get_api_client


def render_api_status():
    """Render API connection status"""
    api = get_api_client()
    health = api.health_check()
    
    if health.get("status") == "healthy":
        st.session_state.api_status = "healthy"
        status_color = "#16a34a"
        status_icon = "✓"
        status_text = "Active"
    elif health.get("status") == "degraded":
        st.session_state.api_status = "degraded"
        status_color = "#ea580c"
        status_icon = "⚠"
        status_text = "Degraded"
    else:
        st.session_state.api_status = "unavailable"
        status_color = "#dc2626"
        status_icon = "✕"
        status_text = "Unavailable"
    
    return status_color, status_icon, status_text


def render_risk_metrics():
    """Render risk assessment metrics"""
    st.markdown('<div class="section-header" style="color: #BACEFF;">⚠️ Risk Assessment</div>', 
                unsafe_allow_html=True)
    
    # Extract from last analysis if available
    last_analysis = st.session_state.get("last_analysis")
    overall_risk = None
    default_prob = None
    confidence = None
    
    if last_analysis and last_analysis.get("risk_analysis"):
        risk_data = last_analysis["risk_analysis"]
        structured_output = risk_data.get("structured_output", {})
        
        # Extract alternatives risk analysis
        alternatives = structured_output.get("alternatives_risk_analysis", [])
        
        if alternatives:
            # Get the highest risk score across all alternatives
            risk_scores = [alt.get("risk_score") for alt in alternatives if alt.get("risk_score") is not None]
            if risk_scores:
                # Convert risk score (0-10) to percentage
                overall_risk = max(risk_scores) * 10
            
            # Get the highest default probability across all alternatives
            default_probs = [alt.get("default_probability") for alt in alternatives if alt.get("default_probability") is not None]
            if default_probs:
                # Convert to percentage (if it's already a decimal like 0.4)
                max_default = max(default_probs)
                default_prob = max_default * 100 if max_default <= 1.0 else max_default
        
        # Get confidence from similarity
        confidence = last_analysis.get("avg_similarity")
        if confidence:
            confidence = confidence * 100
    
    # Only show metrics if we have analysis data
    if overall_risk is None and default_prob is None and confidence is None:
        st.markdown("""
        <div style="font-size: 12px; color: #9CA3AF; text-align: center; padding: 20px;">
            Run a decision analysis to see risk metrics
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display risk score
    if overall_risk is not None:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Overall Risk Score</div>
            <div class="info-value" style="color: #ea580c;">{overall_risk:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display default probability
    if default_prob is not None:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Default Probability</div>
            <div class="info-value" style="color: #16a34a;">{default_prob:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display confidence
    if confidence is not None:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Confidence Level</div>
            <div class="info-value" style="color: #1e40af;">{confidence:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)


def render_data_quality():
    """Render data quality indicators"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">📊 Data Quality</div>', 
                unsafe_allow_html=True)
    
    # Get metrics from API if available
    try:
        api = get_api_client()
        metrics = api.get_metrics()
        
        if metrics:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-label">Total Clients</div>
                <div class="info-value" style="font-size: 16px;">{metrics.get('total_clients', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-card">
                <div class="info-label">Vector Dimension</div>
                <div class="info-value" style="font-size: 16px;">{metrics.get('vector_dimension', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown('<div style="font-size: 12px; color: #9CA3AF;">Metrics unavailable</div>', 
                   unsafe_allow_html=True)


def render_analysis_summary():
    """Render analysis metadata summary"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">📊 Analysis Summary</div>', 
                unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-card">
        <div class="info-label">Total Analyses</div>
        <div class="info-value">{st.session_state.query_count}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-card">
        <div class="info-label">Cases Analyzed</div>
        <div class="info-value">{st.session_state.query_count * 5}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show API status
    status_color, status_icon, status_text = render_api_status()
    
    st.markdown(f"""
    <div class="info-card">
        <div class="info-label">System Status</div>
        <div class="info-value" style="color: {status_color};">{status_icon} {status_text}</div>
    </div>
    """, unsafe_allow_html=True)




def render_best_practices():
    """Render decision-making best practices"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">💡 Best Practices</div>', 
                unsafe_allow_html=True)
    
    tips = [
        "Review all shadow alternatives",
        "Check similar past cases",
        "Compare confidence scores",
        "Validate with domain expertise"
    ]
    
    for tip in tips:
        st.markdown(f'<div class="tip-item">• {tip}</div>', unsafe_allow_html=True)


def render_documentation():
    """Render documentation and help sections"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">📖 Documentation</div>', 
                unsafe_allow_html=True)
    
    with st.expander("System Guide", expanded=False):
        st.markdown("""
        **How Decision Shadows Works:**
        1. Enter or search for a client profile
        2. Describe the decision context
        3. System generates 4 shadow decisions (Approve, Conditional, Reject, Defer)
        4. Retrieves similar past cases using semantic search
        5. Multi-agent analysis: Historical patterns & Risk assessment
        6. Compare outcomes across all alternatives
        
        **Key Features:**
        - Semantic search with LLM understanding
        - Historical pattern analysis
        - Risk scoring for alternatives
        - Real-time similar case retrieval
        """)
    
    with st.expander("Understanding Risk Levels", expanded=False):
        st.markdown("""
        **Risk Score Interpretation:**
        - 0-30%: Low Risk ✓
        - 31-60%: Medium Risk ⚠️
        - 61-100%: High Risk ⛔
        
        **Default Probability:**
        - < 5%: Very Low
        - 5-15%: Low
        - 15-30%: Moderate
        - > 30%: High
        """)
    
    with st.expander("Keyboard Shortcuts", expanded=False):
        st.markdown("""
        - **Ctrl/Cmd + Enter**: Submit query
        - **Escape**: Clear input
        - **?**: Open help
        """)


def render_info_panel():
    """Render complete right info panel"""
    render_risk_metrics()
    render_data_quality()
    render_analysis_summary()
    render_best_practices()
    render_documentation()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.caption("Decision Shadows v1.0 | Powered by RAG API")
