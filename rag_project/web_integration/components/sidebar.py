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
    
    # Search mode selection
    search_mode = st.radio("Search by:", ["Client ID", "Filters"], horizontal=True, key="profile_search_mode")
    
    if search_mode == "Client ID":
        # Client ID search
        col_id, col_search = st.columns([3, 1])
        with col_id:
            # Pre-fill with current client ID if one is loaded
            default_id = str(st.session_state.get("current_client_id", "")) if st.session_state.get("current_client_id") else ""
            client_id_input = st.text_input("Client ID", value=default_id, placeholder="e.g., 100021 or APP-2024-001", key="client_id_input")
        with col_search:
            st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
            search_btn = st.button("🔍", help="Search for client", key="id_search_btn")
    else:
        search_btn = False
        client_id_input = None
    
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
        
        # Display client description/text if available
        client_text = profile_data.get("text", "")
        if client_text and search_mode == "Client ID":
            with st.expander("📄 Client Profile Document", expanded=True):
                st.markdown(f'<div style="background: #1E1E1E; padding: 15px; border-radius: 8px; font-size: 13px; line-height: 1.6; max-height: 400px; overflow-y: auto; color: #E5E7EB;">{client_text}</div>', unsafe_allow_html=True)
    
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
    
    # Filter search button (for "Filters" mode)
    if st.session_state.get("profile_search_mode") == "Filters":
        if st.button("🔍 Search by Filters", use_container_width=True, key="filter_search_btn"):
            try:
                api = get_api_client()
                
                # Build filter dict for API
                filters = {}
                
                # Age filter (convert to DAYS_BIRTH) - must use _range suffix
                filters["DAYS_BIRTH_range"] = {
                    "gte": -(age + 5) * 365,  # Allow ±5 year range
                    "lte": -(age - 5) * 365
                }
                
                # Income filter - must use _range suffix
                filters["AMT_INCOME_TOTAL_range"] = {
                    "gte": income * 0.8,  # Allow ±20% range
                    "lte": income * 1.2
                }
                
                # Education filter (if not default)
                if education != "High School":
                    filters["NAME_EDUCATION_TYPE"] = education
                
                # Employment filter (if not default)
                if employment != "Stable":
                    filters["NAME_INCOME_TYPE"] = employment
                
                with st.spinner("Searching for matching clients..."):
                    # Use metadata search for filter-only search
                    results = api.search_metadata(filters=filters, top_k=10)
                
                if results and results.get("results"):
                    st.success(f"✓ Found {len(results['results'])} matching clients")
                    st.session_state.filter_search_results = results
                    
                    # Display results
                    with st.expander(f"📊 {len(results['results'])} Matching Clients", expanded=True):
                        for idx, result in enumerate(results["results"][:5], 1):  # Show top 5
                            result_client_id = result.get("client_id", "Unknown")
                            similarity = result.get("score", result.get("similarity", 0))
                            result_metadata = result.get("metadata", {})
                            result_age = int(result_metadata.get("DAYS_BIRTH", -12775) / -365) if result_metadata.get("DAYS_BIRTH") else "N/A"
                            result_income = result_metadata.get("AMT_INCOME_TOTAL", "N/A")
                            
                            st.markdown(f"""
                            <div style="background: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 8px;">
                                <div style="color: #60A5FA; font-weight: 600;">Client {result_client_id}</div>
                                <div style="font-size: 12px; color: #9CA3AF;">
                                    Age: {result_age} | Income: ${result_income:,} | Match: {similarity*100:.1f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add button to view this client
                            if st.button(f"👁️ View Client {result_client_id}", key=f"view_filter_{result_client_id}", use_container_width=True):
                                # Fetch full profile from API
                                profile_data = api.get_profile(result_client_id)
                                if profile_data and profile_data.get("client_id"):
                                    st.session_state.current_client_id = result_client_id
                                    st.session_state.current_profile = profile_data
                                    st.session_state.profile_search_mode = "Client ID"  # Switch to ID mode to show profile
                                    st.rerun()
                else:
                    st.warning("No matching clients found. Try adjusting the criteria.")
                    
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
    
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
        col_info, col_actions = st.columns([3, 1])
        
        with col_info:
            st.markdown(f"""
            <div style="background: #F9FAFB; padding: 10px; border-radius: 6px; font-size: 12px;">
                <strong>📄 {uploaded_file.name}</strong><br/>
                <span style="color: #6B7280;">Size: {uploaded_file.size / 1024:.1f} KB</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            st.markdown('<div style="margin-top: 6px;"></div>', unsafe_allow_html=True)
            
        # Action buttons in a row
        col_search, col_analyze = st.columns(2)
        
        with col_search:
            if st.button("🔍 Search", key="pdf_search_btn", use_container_width=True):
                try:
                    from api_client import get_api_client
                    api = get_api_client()
                    
                    with st.spinner("Extracting text from PDF and searching..."):
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        # Search using PDF
                        results = api.search_pdf(uploaded_file, top_k=5)
                    
                    if results and results.get("results"):
                        st.session_state.pdf_search_results = results["results"]
                        st.session_state.last_pdf_query = uploaded_file.name
                        st.session_state.pdf_understanding = results.get("understanding")
                        
                        # Show results summary in a row
                        col_found, col_pages = st.columns(2)
                        with col_found:
                            st.success(f"✓ Found {results.get('total_results', 0)} similar cases")
                        with col_pages:
                            if results.get("understanding"):
                                understanding = results["understanding"]
                                st.info(f"📄 Extracted {understanding.get('pages_extracted', 0)} page(s)")
                    else:
                        st.warning("No similar cases found")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col_analyze:
            if st.button("📊 Analyze", key="pdf_analyze_btn", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Preparing PDF for analysis..."):
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        # Store PDF for analysis using the correct session state keys
                        st.session_state.analyze_pdf_trigger = True
                        st.session_state.analyze_pdf_file = uploaded_file
                        
                        st.success(f"✓ PDF ready for analysis")
                        st.rerun()
                        
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
                
                # Make profile clickable with view and analyze buttons
                col_info, col_view, col_analyze = st.columns([3, 1, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="background: #F9FAFB; padding: 8px; border-radius: 6px; margin-bottom: 6px; font-size: 11px;">
                        <div style="font-weight: 600; color: #1F2937;">Client {client_id}</div>
                        <div style="color: #6B7280;">Similarity: {similarity}% | Outcome: <span style="color: {outcome_color};">{outcome_text}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_view:
                    if st.button("👁️", key=f"view_pdf_client_{client_id}_{idx}", help="View profile details"):
                        st.session_state.current_client_id = client_id
                        st.session_state.current_profile = result
                        st.rerun()
                with col_analyze:
                    if st.button("📊", key=f"analyze_pdf_client_{client_id}_{idx}", help="Run full analysis"):
                        st.session_state.analyze_client_id = client_id
                        st.session_state.analyze_trigger = True
                        st.session_state.current_client_id = client_id
                        st.session_state.current_profile = result
                        st.rerun()



def render_image_upload():
    """Render image upload and search section"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="color: #BACEFF;">🖼️ Image Search</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 12px; color: #6B7280; margin-bottom: 10px;">
        Upload one or multiple images to find similar clients based on combined content (OCR)
    </div>
    """, unsafe_allow_html=True)
    
    # Image Upload - Now supports multiple files
    uploaded_files = st.file_uploader(
        "📤 Upload Image Document(s)",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        key="image_upload",
        accept_multiple_files=True,
        help="Upload one or more images, then click the Search button"
    )
    
    if uploaded_files:
        # Display all uploaded files
        total_size = sum(f.size for f in uploaded_files) / 1024
        
        col_info, col_search = st.columns([3, 1])
        
        with col_info:
            if len(uploaded_files) == 1:
                st.markdown(f"""
                <div style="background: #F9FAFB; padding: 10px; border-radius: 6px; font-size: 12px;">
                    <strong>🖼️ {uploaded_files[0].name}</strong><br/>
                    <span style="color: #6B7280;">Size: {uploaded_files[0].size / 1024:.1f} KB</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #F9FAFB; padding: 10px; border-radius: 6px; font-size: 12px;">
                    <strong>🖼️ {len(uploaded_files)} images selected</strong><br/>
                    <span style="color: #6B7280;">Total size: {total_size:.1f} KB</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col_search:
            st.markdown('<div style="margin-top: 6px;"></div>', unsafe_allow_html=True)
            if st.button("🔍 Search", key="image_search_btn", use_container_width=True, type="primary"):
                try:
                    from api_client import get_api_client
                    api = get_api_client()
                    
                    with st.spinner(f"Extracting text from {len(uploaded_files)} image(s) and searching..."):
                        # Process multiple images
                        all_results = []
                        combined_text = []
                        
                        for uploaded_file in uploaded_files:
                            # Reset file pointer
                            uploaded_file.seek(0)
                            
                            # Search using Image
                            results = api.search_image(uploaded_file, top_k=5)
                            
                            if results and results.get("results"):
                                all_results.extend(results["results"])
                    
                    if all_results:
                        # Remove duplicates and sort by score
                        seen_clients = {}
                        for result in all_results:
                            client_id = result.get("client_id")
                            score = result.get("score", 0)
                            if client_id not in seen_clients or score > seen_clients[client_id].get("score", 0):
                                seen_clients[client_id] = result
                        
                        # Sort by score descending
                        unique_results = sorted(seen_clients.values(), 
                                              key=lambda x: x.get("score", 0), 
                                              reverse=True)[:5]
                        
                        st.session_state.image_search_results = unique_results
                        st.session_state.last_image_query = f"{len(uploaded_files)} image(s)"
                        
                        # Show results summary
                        st.success(f"✓ Found {len(unique_results)} similar cases from {len(uploaded_files)} image(s)")
                    else:
                        st.warning("No similar cases found")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Display results if available
        if st.session_state.get("image_search_results"):
            st.markdown('<div style="margin-top: 15px;"><small style="color: #6B7280;">Search Results</small></div>', 
                       unsafe_allow_html=True)
            
            for idx, result in enumerate(st.session_state.image_search_results[:3], 1):
                score = result.get("score", 0)
                similarity = int(score * 100) if score and score <= 1 else int(score) if score else 85
                client_id = result.get("client_id", "Unknown")
                target = result.get("target", 0)
                
                outcome_color = "#16a34a" if target == 0 else "#dc2626"
                outcome_text = "Good" if target == 0 else "Default"
                
                # Make profile clickable with view and analyze buttons
                col_info, col_view, col_analyze = st.columns([3, 1, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="background: #F9FAFB; padding: 8px; border-radius: 6px; margin-bottom: 6px; font-size: 11px;">
                        <div style="font-weight: 600; color: #1F2937;">Client {client_id}</div>
                        <div style="color: #6B7280;">Similarity: {similarity}% | Outcome: <span style="color: {outcome_color};">{outcome_text}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_view:
                    if st.button("👁️", key=f"view_image_client_{client_id}_{idx}", help="View profile details"):
                        st.session_state.current_client_id = client_id
                        st.session_state.current_profile = result
                        st.rerun()
                with col_analyze:
                    if st.button("📊", key=f"analyze_image_client_{client_id}_{idx}", help="Run full analysis"):
                        st.session_state.analyze_client_id = client_id
                        st.session_state.analyze_trigger = True
                        st.rerun()


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
    
    
    return {
        "num_similar_cases": num_similar_cases,
        "risk_threshold": risk_threshold,
    }


def render_advanced_options():
    """Render advanced analysis options"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    return {
            "use_llm": True,
            "show_details": True
        }


def render_left_sidebar():
    """Render complete left sidebar"""
    client_profile = render_client_profile()
    render_pdf_upload()
    render_image_upload()
    settings = render_analysis_settings()
    advanced = render_advanced_options()
    
    return client_profile, settings, advanced
