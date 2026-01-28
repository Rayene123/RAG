import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="Decision Shadows",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Multimodal RAG System for Pre-Decision Analysis"}
)

# Custom CSS styling
st.markdown("""
<style>
    /* Decision Shadows color palette */
    :root {
        --primary: #1e40af;
        --success: #16a34a;
        --warning: #ea580c;
        --error: #dc2626;
        --info: #0891b2;
        --bg-light: #f8fafc;
        --border: #cbd5e1;
        --text-primary: #0f172a;
        --text-secondary: #475569;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #1e40af 0%, #0891b2 100%);
        padding: 25px 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        color: white;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-container p {
        margin: 8px 0 0 0;
        font-size: 13px;
        opacity: 0.92;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #E5E7EB;
        color: #1F2937;
    }
    
    /* Card styling */
    .result-card {
        background: white;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #0066CC;
    }
    
    .result-title {
        font-size: 15px;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 8px;
    }
    
    .result-excerpt {
        font-size: 13px;
        color: #6B7280;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    
    .result-meta {
        font-size: 12px;
        color: #9CA3AF;
    }
    
    .relevance-score {
        display: inline-block;
        background: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Upload area */
    .upload-box {
        border: 2px dashed #0066CC;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background: #F0F9FF;
        margin-bottom: 15px;
    }
    
    /* Document list */
    .doc-item {
        background: #F9FAFB;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
    }
    
    .doc-status {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .status-indexed {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .status-processing {
        background: #FEF3C7;
        color: #92400E;
    }
    
    /* Response area */
    .response-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 15px;
    }
    
    .response-text {
        font-size: 14px;
        line-height: 1.8;
        color: #1F2937;
    }
    
    /* Info panel */
    .info-card {
        background: #F9FAFB;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 4px solid #0066CC;
    }
    
    .info-label {
        font-size: 12px;
        color: #6B7280;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    .info-value {
        font-size: 18px;
        font-weight: 700;
        color: #1F2937;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.35);
    }
    
    /* Shadow decision badges */
    .shadow-approve {
        background: #d1fae5;
        border-left: 4px solid #16a34a;
        color: #065f46;
    }
    
    .shadow-reject {
        background: #fee2e2;
        border-left: 4px solid #dc2626;
        color: #7f1d1d;
    }
    
    .shadow-conditional {
        background: #fef3c7;
        border-left: 4px solid #ea580c;
        color: #78350f;
    }
    
    .shadow-defer {
        background: #e0e7ff;
        border-left: 4px solid #1e40af;
        color: #312e81;
    }
    
    /* Risk/Bias indicators */
    .risk-high {
        background: #fecaca;
        color: #7f1d1d;
    }
    
    .risk-medium {
        background: #fcd34d;
        color: #78350f;
    }
    
    .risk-low {
        background: #86efac;
        color: #166534;
    }
    
    .bias-indicator {
        padding: 10px 12px;
        border-radius: 6px;
        font-size: 13px;
        margin-bottom: 10px;
    }
    
    /* Comparison card */
    .comparison-card {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        background: white;
    }
    
    .comparison-card:hover {
        border-color: #1e40af;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.1);
    }
    
    .comparison-header {
        font-weight: 600;
        margin-bottom: 8px;
        color: #0f172a;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0066CC;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #6B7280;
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    /* Loading animation */
    .loading-text {
        display: inline-block;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: #E5E7EB;
        margin: 20px 0;
    }
    
    /* Tips section */
    .tip-item {
        background: #FEF3C7;
        border-left: 3px solid #F59E0B;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 13px;
        color: #78350F;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "documents" not in st.session_state:
    st.session_state.documents = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# Header Section
st.markdown("""
<div class="header-container">
    <h1>⚖️ Decision Shadows</h1>
    <p>Multimodal RAG System for Pre-Decision Analysis | Financial Risk & Compliance</p>
</div>
""", unsafe_allow_html=True)

# Main Layout - 3 Columns
col_sidebar, col_main, col_info = st.columns([1.15, 2.4, 1.2])

# ============================================================================
# LEFT SIDEBAR - Client Profile & Decision Inputs
# ============================================================================
with col_sidebar:
    st.markdown('<div class="section-header" style="color: #BACEFF;">👤 Client Profile</div>', unsafe_allow_html=True)
    
    
    # Client Information Input
    client_id = st.text_input("Client ID", placeholder="e.g., APP-2024-001")
    client_name = st.text_input("Client Name", placeholder="John Smith")
    
    col_age, col_income = st.columns(2)
    with col_age:
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
    with col_income:
        income = st.number_input("Income ($)", min_value=0, value=50000, step=1000)
    
    education = st.selectbox("Education", ["High School", "Bachelor", "Master", "PhD"])
    employment = st.selectbox("Employment Status", ["Stable", "Self-Employed", "Contract", "Seeking"])
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header" style="color: #BACEFF;">📚 Supporting Documents</div>', unsafe_allow_html=True)
    
    # Upload Section
    st.markdown('<div class="upload-box">Drag and drop documents or click below</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, DOCX, TXT)",
        accept_multiple_files=True,
        key="doc_upload",
        label_visibility="collapsed"
    )
    
    # Process uploaded files
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in [doc['name'] for doc in st.session_state.documents]:
                st.session_state.documents.append({
                    'name': file.name,
                    'size': file.size,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'status': 'Indexed'
                })
    
    # Display uploaded documents
    if st.session_state.documents:
        st.markdown('<div style="margin-top: 20px; margin-bottom: 10px;"><small style="color: #6B7280;">Indexed Documents</small></div>', 
                   unsafe_allow_html=True)
        
        for doc in st.session_state.documents:
            col_doc, col_delete = st.columns([4, 1])
            with col_doc:
                status_class = "status-indexed" if doc['status'] == 'Indexed' else "status-processing"
                st.markdown(f"""
                <div class="doc-item">
                    <div>
                        <div style="font-weight: 600; color: #1F2937;">{doc['name']}</div>
                        <div style="color: #9CA3AF; font-size: 12px;">{doc['date']}</div>
                    </div>
                    <div class="doc-status {status_class}">{doc['status']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_delete:
                if st.button("✕", key=f"del_{doc['name']}"):
                    st.session_state.documents = [d for d in st.session_state.documents if d['name'] != doc['name']]
                    st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📁</div>
            <p><small>No documents uploaded yet</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Decision Settings
    st.markdown('<div class="section-header" style="color: #BACEFF;">⚙️ Analysis Settings</div>', unsafe_allow_html=True)
    
    num_similar_cases = st.slider(
        "Similar Cases to Retrieve",
        min_value=2,
        max_value=10,
        value=5,
        help="Number of past cases to reference"
    )
    
    risk_threshold = st.slider(
        "Risk Tolerance (%)",
        min_value=0,
        max_value=100,
        value=50,
        help="Your acceptable risk level (0=Conservative, 100=Aggressive)"
    )
    
    search_type = st.selectbox(
        "Multimodal Search",
        ["Text + Numbers", "Text + Images", "Full Multimodal"],
        help="Types of data to include in analysis"
    )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Advanced Options
    with st.expander("🔧 Advanced Analysis"):
        st.subheader("Agent Settings")
        historian_weight = st.slider("Historian (Past Patterns)", 0.0, 1.0, 0.8)
        risk_weight = st.slider("Risk Agent (Score)", 0.0, 1.0, 0.9)
        bias_weight = st.slider("Bias Detection", 0.0, 1.0, 0.85)
        explainer_detail = st.selectbox("Explanation Level", ["Brief", "Standard", "Detailed"])
        
        st.divider()
        
        include_simulation = st.checkbox("Run Outcome Simulation", value=True)
        detect_bias = st.checkbox("Full Bias Analysis", value=True)
        show_sources = st.checkbox("Show Case Citations", value=True)

# ============================================================================
# MAIN CONTENT AREA - Shadow Generation & Analysis
# ============================================================================
with col_main:
    # Decision Analysis Section
    st.markdown('<div class="section-header" style="color: #BACEFF;">⚖️ Generate Shadow Decisions</div>', unsafe_allow_html=True)
    
    decision_context = st.text_area(
        "Decision Context",
        placeholder="Describe the decision context, business case, or application summary...",
        height=80,
        label_visibility="collapsed",
        key="decision_input"
    )
    
    col_analyze, col_reset = st.columns([3, 1])
    with col_analyze:
        analyze_btn = st.button(
            "🔮 Analyze & Generate Shadows",
            use_container_width=True,
            type="primary"
        )
    
    with col_reset:
        if st.button("Reset", use_container_width=True):
            st.session_state.last_query = ""
            st.rerun()
    
    # Quick templates
    with st.expander("📋 Decision Templates", expanded=False):
        templates = {
            "Loan Application": "Income: $50k, Payment history: Good, Employment: Stable",
            "Credit Extension": "Current balance: $5k, Utilization: 60%, Payment history: Excellent",
            "Risk Assessment": "Industry: Tech, Size: Startup, Age: 2 years",
            "Compliance Check": "Jurisdiction: US, Regulatory status: Clean, AML screening: Pass"
        }
        for template_name, template_text in templates.items():
            if st.button(template_name, key=f"tmpl_{template_name}", use_container_width=True):
                st.session_state.last_query = template_text
                st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Shadow Generation Results
    if analyze_btn and decision_context:
        st.session_state.query_count += 1
        st.session_state.last_query = decision_context
        
        st.markdown('<div class="section-header">🔮 Shadow Decision Alternatives</div>', unsafe_allow_html=True)
        
        # Simulate processing
        with st.spinner("Generating shadow decisions and analyzing alternatives..."):
            time.sleep(2)
        
        st.success(f"Analysis complete | Found {num_similar_cases} similar past cases")
        
        # Shadow Decisions Display
        shadows = [
            {"decision": "APPROVE", "confidence": 78, "risk": "Low", "probability": "High", "cases": 12},
            {"decision": "CONDITIONAL APPROVE", "confidence": 85, "risk": "Medium", "probability": "Very High", "cases": 8},
            {"decision": "REJECT", "confidence": 65, "risk": "High", "probability": "Medium", "cases": 5},
            {"decision": "DEFER", "confidence": 72, "risk": "Medium", "probability": "Medium", "cases": 3}
        ]
        
        # Create tabs for each shadow
        tab_approve, tab_conditional, tab_reject, tab_defer = st.tabs(
            ["✅ Approve", "⚠️ Conditional", "❌ Reject", "⏸️ Defer"]
        )
        
        with tab_approve:
            st.markdown(f"""
            <div class="shadow-approve bias-indicator">
                <div style="font-weight: 600; margin-bottom: 8px;">Approval Decision</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                    <div><strong>Confidence:</strong> {shadows[0]['confidence']}%</div>
                    <div><strong>Risk Level:</strong> {shadows[0]['risk']}</div>
                    <div><strong>Success Probability:</strong> {shadows[0]['probability']}</div>
                    <div><strong>Similar Cases:</strong> {shadows[0]['cases']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("**Rationale:** Strong financial profile with stable income and excellent payment history. Similar cases show 85% success rate.")
        
        with tab_conditional:
            st.markdown(f"""
            <div class="shadow-conditional bias-indicator">
                <div style="font-weight: 600; margin-bottom: 8px;">Conditional Approval</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                    <div><strong>Confidence:</strong> {shadows[1]['confidence']}%</div>
                    <div><strong>Risk Level:</strong> {shadows[1]['risk']}</div>
                    <div><strong>Success Probability:</strong> {shadows[1]['probability']}</div>
                    <div><strong>Similar Cases:</strong> {shadows[1]['cases']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("**Conditions:**\n- Lower initial credit limit: $3,000\n- Monthly reviews for 6 months\n- Income verification every quarter")
        
        with tab_reject:
            st.markdown(f"""
            <div class="shadow-reject bias-indicator">
                <div style="font-weight: 600; margin-bottom: 8px;">Rejection Decision</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                    <div><strong>Confidence:</strong> {shadows[2]['confidence']}%</div>
                    <div><strong>Risk Level:</strong> {shadows[2]['risk']}</div>
                    <div><strong>Success Probability:</strong> {shadows[2]['probability']}</div>
                    <div><strong>Similar Cases:</strong> {shadows[2]['cases']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("**Concerns:** Recent delinquency patterns. Historical data shows 70% default rate for similar profiles.")
        
        with tab_defer:
            st.markdown(f"""
            <div class="shadow-defer bias-indicator">
                <div style="font-weight: 600; margin-bottom: 8px;">Defer Decision</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                    <div><strong>Confidence:</strong> {shadows[3]['confidence']}%</div>
                    <div><strong>Risk Level:</strong> {shadows[3]['risk']}</div>
                    <div><strong>Success Probability:</strong> {shadows[3]['probability']}</div>
                    <div><strong>Similar Cases:</strong> {shadows[3]['cases']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("**Recommendation:** Wait for 6-month employment history. Request updated financial statements.")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📚 Similar Past Cases</div>', unsafe_allow_html=True)
        
        # Similar Cases
        cases = [
            {"id": "CASE-2024-001", "similarity": 92, "decision": "APPROVED", "outcome": "Performing", "timeframe": "18 months ago"},
            {"id": "CASE-2024-015", "similarity": 88, "decision": "CONDITIONAL", "outcome": "Performing", "timeframe": "12 months ago"},
            {"id": "CASE-2023-089", "similarity": 85, "decision": "APPROVED", "outcome": "Performing", "timeframe": "8 months ago"},
            {"id": "CASE-2023-142", "similarity": 81, "decision": "REJECTED", "outcome": "N/A", "timeframe": "6 months ago"},
            {"id": "CASE-2023-201", "similarity": 78, "decision": "DEFERRED", "outcome": "Later Approved", "timeframe": "4 months ago"},
        ]
        
        for case in cases[:num_similar_cases]:
            outcome_color = "#16a34a" if case["outcome"] in ["Performing", "Later Approved"] else "#666"
            st.markdown(f"""
            <div class="comparison-card">
                <div class="comparison-header">Case {case['id']} - {case['similarity']}% Similar</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 12px;">
                    <div><strong>Decision:</strong> {case['decision']}</div>
                    <div><strong>Outcome:</strong> <span style="color: {outcome_color}">{case['outcome']}</span></div>
                    <div><strong>Timeframe:</strong> {case['timeframe']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif decision_context and not analyze_btn:
        st.info("Click 'Analyze & Generate Shadows' to run the analysis")
    
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">⚖️</div>
            <p><small>Enter client profile and decision context to generate shadow alternatives</small></p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# RIGHT SIDEBAR - Risk & Bias Analysis
# ============================================================================
with col_info:
    st.markdown('<div class="section-header" style="color: #BACEFF;">⚠️ Risk Assessment</div>', unsafe_allow_html=True)
    # Risk Metrics
    st.markdown(f"""
    <div class="info-card">
        <div class="info-label">Overall Risk Score</div>
        <div class="info-value" style="color: #ea580c;">42%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-card">
        <div class="info-label">Default Probability</div>
        <div class="info-value" style="color: #16a34a;">8.2%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-card">
        <div class="info-label">Confidence Level</div>
        <div class="info-value" style="color: #1e40af;">78%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Bias Detection
    st.markdown('<div class="section-header" style="color: #BACEFF;">🔍 Bias Detection</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="bias-indicator risk-low">
        <strong>Age Bias:</strong> Low ✓
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="bias-indicator risk-low">
        <strong>Gender Bias:</strong> Low ✓
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="bias-indicator risk-medium">
        <strong>Income Bias:</strong> Medium ⚠️
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="bias-indicator risk-low">
        <strong>Location Bias:</strong> Low ✓
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Analysis Metadata
    st.markdown('<div class="section-header" style="color: #BACEFF;">📊 Analysis Summary</div>', unsafe_allow_html=True)
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
    
    st.markdown("""
    <div class="info-card">
        <div class="info-label">System Status</div>
        <div class="info-value" style="color: #16a34a;">✓ Active</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Decision Tips
    st.markdown('<div class="section-header" style="color: #BACEFF;">💡 Best Practices</div>', unsafe_allow_html=True)
    tips = [
        "Review all shadow alternatives",
        "Check similar past cases",
        "Consider bias detection alerts",
        "Validate with domain expertise"
    ]
    
    for tip in tips:
        st.markdown(f'<div class="tip-item">• {tip}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Documentation
    st.markdown('<div class="section-header" style="color: #BACEFF;">📖 Documentation</div>', unsafe_allow_html=True)
    with st.expander("System Guide", expanded=False):
        st.markdown("""
        **How Decision Shadows Works:**
        1. Enter client profile and decision context
        2. System generates 4 shadow decisions (Approve, Conditional, Reject, Defer)
        3. Retrieves similar past cases from multimodal database
        4. Agents analyze: Historical patterns, Risk scores, Bias indicators, Explanations
        5. Compare outcomes across all alternatives
        
        **Key Features:**
        - Multimodal RAG (text, PDFs, images, numbers)
        - Outcome simulation for each alternative
        - Explainable AI recommendations
        - Continuous learning from decisions
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
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Footer
    st.caption("RAG Assistant v1.0 | Last updated: Jan 2026")
