"""
Left Sidebar Components - Client Profile & Document Management
"""
import streamlit as st
from datetime import datetime
from api_client import get_api_client


def render_client_profile():
    """Render client profile input section"""
    st.markdown('<div class="section-header" style="color: #BACEFF;">👤 Client Profile</div>', 
                unsafe_allow_html=True)
    
    # Client ID search
    col_id, col_search = st.columns([3, 1])
    with col_id:
        client_id_input = st.text_input("Client ID", placeholder="e.g., 100021 or APP-2024-001", key="client_id_input")
    with col_search:
        st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
        search_btn = st.button("🔍", help="Search for client")
    
    # Initialize profile data
    client_id = None
    age = 35
    income = 50000
    education = "High School"
    employment = "Stable"
    
    # If search button clicked, try to fetch from API
    if search_btn and client_id_input:
        try:
            # Try to parse as integer for client_id
            client_id = int(client_id_input)
            api = get_api_client()
            
            with st.spinner(f"Searching for client {client_id}..."):
                profile_data = api.get_profile(client_id)
            
            if profile_data and profile_data.get("client_id"):
                st.success(f"✓ Found client {client_id}")
                st.session_state.current_client_id = client_id
                st.session_state.current_profile = profile_data
                
                # Display client description/text
                client_text = profile_data.get("text", "")
                if client_text:
                    with st.expander("📄 Client Profile Document", expanded=True):
                        st.markdown(f'<div style="background: #1E1E1E; padding: 15px; border-radius: 8px; font-size: 13px; line-height: 1.6; max-height: 400px; overflow-y: auto; color: #E5E7EB;">{client_text}</div>', unsafe_allow_html=True)
                
                # Extract metadata
                metadata = profile_data.get("metadata", {})
                
                # Try to extract common fields
                age = int(metadata.get("DAYS_BIRTH", -12775) / -365) if metadata.get("DAYS_BIRTH") else 35
                income = metadata.get("AMT_INCOME_TOTAL", 50000)
                
                # Map education if available
                education_code = metadata.get("NAME_EDUCATION_TYPE")
                if education_code:
                    education = education_code
                
                # Map employment
                employment_code = metadata.get("NAME_INCOME_TYPE", "Stable")
                employment = employment_code
                
            else:
                st.error(f"Client {client_id} not found")
        except ValueError:
            st.error("Please enter a valid numeric Client ID")
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
    
    # Use stored profile if available
    elif st.session_state.get("current_profile"):
        profile_data = st.session_state.current_profile
        client_id = profile_data.get("client_id")
        metadata = profile_data.get("metadata", {})
        age = int(metadata.get("DAYS_BIRTH", -12775) / -365) if metadata.get("DAYS_BIRTH") else 35
        income = metadata.get("AMT_INCOME_TOTAL", 50000)
        education = metadata.get("NAME_EDUCATION_TYPE", "High School")
        employment = metadata.get("NAME_INCOME_TYPE", "Stable")
    
    # Manual input fields (can be edited even after loading)
    if not client_id and client_id_input:
        client_id = client_id_input
    
    col_age, col_income = st.columns(2)
    with col_age:
        age = st.number_input("Age", min_value=18, max_value=100, value=int(age), key="age_input")
    with col_income:
        income = st.number_input("Income ($)", min_value=0, value=int(income), step=1000, key="income_input")
    
    education = st.selectbox("Education", ["High School", "Bachelor", "Master", "PhD", "Secondary / secondary special", "Higher education", "Incomplete higher", "Lower secondary"], 
                            index=0 if not education else (["High School", "Bachelor", "Master", "PhD", "Secondary / secondary special", "Higher education", "Incomplete higher", "Lower secondary"].index(education) if education in ["High School", "Bachelor", "Master", "PhD", "Secondary / secondary special", "Higher education", "Incomplete higher", "Lower secondary"] else 0),
                            key="education_input")
    employment = st.selectbox("Employment Status", ["Stable", "Self-Employed", "Contract", "Seeking", "Working", "Commercial associate", "Pensioner", "State servant", "Unemployed"], 
                              index=0 if not employment else (["Stable", "Self-Employed", "Contract", "Seeking", "Working", "Commercial associate", "Pensioner", "State servant", "Unemployed"].index(employment) if employment in ["Stable", "Self-Employed", "Contract", "Seeking", "Working", "Commercial associate", "Pensioner", "State servant", "Unemployed"] else 0),
                              key="employment_input")
    
    return {
        "client_id": client_id,
        "age": age,
        "income": income,
        "education": education,
        "employment": employment
    }


def render_pdf_upload():
    """Render PDF upload and search section"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">📄 PDF Search</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 12px; color: #6B7280; margin-bottom: 10px;">
        Upload a PDF to find similar clients based on document content
    </div>
    """, unsafe_allow_html=True)
    
    # PDF Upload
    uploaded_file = st.file_uploader(
        "📤 Upload PDF Document",
        type=['pdf'],
        key="pdf_upload",
        help="Upload a PDF, then click the Search button that appears"
    )
    
    if uploaded_file is not None:
        col_info, col_search = st.columns([3, 1])
        
        with col_info:
            st.markdown(f"""
            <div style="background: #F9FAFB; padding: 10px; border-radius: 6px; font-size: 12px;">
                <strong>📄 {uploaded_file.name}</strong><br/>
                <span style="color: #6B7280;">Size: {uploaded_file.size / 1024:.1f} KB</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_search:
            st.markdown('<div style="margin-top: 6px;"></div>', unsafe_allow_html=True)
            if st.button("🔍 Search", key="pdf_search_btn", use_container_width=True, type="primary"):
                try:
                    from api_client import get_api_client
                    api = get_api_client()
                    
                    with st.spinner("Extracting text from PDF and searching..."):
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        # Search using PDF
                        results = api.search_pdf(uploaded_file, top_k=5)
                    
                    if results and results.get("results"):
                        st.success(f"✓ Found {results.get('total_results', 0)} similar cases")
                        st.session_state.pdf_search_results = results["results"]
                        st.session_state.last_pdf_query = uploaded_file.name
                        
                        # Show understanding info if available
                        if results.get("understanding"):
                            understanding = results["understanding"]
                            st.info(f"📄 Extracted {understanding.get('pages_extracted', 0)} page(s)")
                    else:
                        st.warning("No similar cases found")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Display results if available
        if st.session_state.get("pdf_search_results"):
            st.markdown('<div style="margin-top: 15px;"><small style="color: #6B7280;">Search Results</small></div>', 
                       unsafe_allow_html=True)
            
            for idx, result in enumerate(st.session_state.pdf_search_results[:3], 1):
                score = result.get("score", 0)
                similarity = int(score * 100) if score and score <= 1 else int(score) if score else 85
                client_id = result.get("client_id", "Unknown")
                target = result.get("target", 0)
                
                outcome_color = "#16a34a" if target == 0 else "#dc2626"
                outcome_text = "Good" if target == 0 else "Default"
                
                st.markdown(f"""
                <div style="background: #F9FAFB; padding: 8px; border-radius: 6px; margin-bottom: 6px; font-size: 11px;">
                    <div style="font-weight: 600; color: #1F2937;">Client {client_id}</div>
                    <div style="color: #6B7280;">Similarity: {similarity}% | Outcome: <span style="color: {outcome_color};">{outcome_text}</span></div>
                </div>
                """, unsafe_allow_html=True)


def render_analysis_settings():
    """Render analysis configuration settings"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">⚙️ Analysis Settings</div>', 
                unsafe_allow_html=True)
    
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
    
    return {
        "num_similar_cases": num_similar_cases,
        "risk_threshold": risk_threshold,
        "search_type": search_type
    }


def render_advanced_options():
    """Render advanced analysis options"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    with st.expander("🔧 Advanced Options"):
        st.markdown("**Query Understanding**")
        use_llm = st.checkbox("Enable LLM Query Understanding", value=True, 
                             help="Use AI to better understand and parse your query")
        
        st.markdown("**Display Options**")
        show_details = st.checkbox("Show Detailed Analysis", value=True)
        
        return {
            "use_llm": use_llm,
            "show_details": show_details
        }


def render_left_sidebar():
    """Render complete left sidebar"""
    client_profile = render_client_profile()
    render_pdf_upload()
    settings = render_analysis_settings()
    advanced = render_advanced_options()
    
    return client_profile, settings, advanced
