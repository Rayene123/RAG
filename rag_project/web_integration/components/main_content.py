"""
Main Content Area Components - Shadow Generation & Analysis
"""
import streamlit as st
from api_client import get_api_client


def render_decision_templates():
    """Render quick decision templates"""
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
                st.session_state.decision_input = template_text  # Update textarea key directly
                st.rerun()


def render_shadow_decision_tab(shadow_data, shadow_type):
    """Render individual shadow decision tab"""
    style_class_map = {
        "APPROVE": "shadow-approve",
        "CONDITIONAL APPROVE": "shadow-conditional",
        "REJECT": "shadow-reject",
        "DEFER": "shadow-defer"
    }
    
    style_class = style_class_map.get(shadow_data["decision"], "shadow-defer")
    
    # Display metrics
    st.markdown(f"""
    <div class="{style_class} bias-indicator">
        <div style="font-weight: 600; margin-bottom: 8px;">{shadow_data['decision']} Decision</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
            <div><strong>Risk Score:</strong> {shadow_data.get('risk_score', 'N/A')}/10</div>
            <div><strong>Risk Level:</strong> {shadow_data['risk']}</div>
            <div><strong>Default Probability:</strong> {shadow_data.get('default_probability', 'N/A')}</div>
            <div><strong>Similar Cases:</strong> {shadow_data['cases']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display agent-generated analysis
    if shadow_data.get('analysis_text'):
        st.markdown("**🤖 Agent Analysis:**")
        st.info(shadow_data['analysis_text'])
    
    # Display risk factors if available
    risk_factors = shadow_data.get('risk_factors', [])
    if risk_factors:
        st.markdown("**⚠️ Risk Factors:**")
        for factor in risk_factors:
            st.markdown(f"- {factor}")
    
    # Display mitigation strategies if available
    mitigation = shadow_data.get('mitigation_strategy')
    if mitigation:
        st.markdown("**🛡️ Mitigation Strategy:**")
        st.success(mitigation)


def render_similar_cases(num_cases, similar_cases_data=None):
    """Render similar past cases section"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📚 Similar Past Cases</div>', unsafe_allow_html=True)
    
    # Use real data if available, otherwise show no cases message
    if similar_cases_data and len(similar_cases_data) > 0:
        for idx, case in enumerate(similar_cases_data[:num_cases], 1):
            # Extract data from API response
            client_id = case.get("client_id", f"UNKNOWN-{idx}")
            score = case.get("score", 0)
            similarity = int(score * 100) if score and score <= 1 else int(score) if score else 85
            metadata = case.get("metadata", {})
            target = case.get("target", metadata.get("target", 0))
            
            # Determine decision and outcome from target
            if target == 0:
                decision = "APPROVED"
                outcome = "Performing"
                outcome_color = "#16a34a"
            else:
                decision = "REJECTED/DEFAULTED"
                outcome = "Non-Performing"
                outcome_color = "#dc2626"
            
            # Extract full text and preview
            full_text = case.get("text", "No description available")
            text_preview = full_text[:100] + "..." if len(full_text) > 100 else full_text
            
            # Create expander for each case
            with st.expander(f"🔍 Client {client_id} - {similarity}% Similar", expanded=False):
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 13px; margin-bottom: 12px; padding: 10px; background: #1E1E1E; border-radius: 6px;">
                    <div><strong>Decision:</strong> {decision}</div>
                    <div><strong>Outcome:</strong> <span style="color: {outcome_color}">{outcome}</span></div>
                    <div><strong>Target:</strong> {target}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**📄 Full Profile Description:**")
                st.markdown(f'<div style="background: #0D1117; padding: 15px; border-radius: 8px; font-size: 13px; line-height: 1.6; max-height: 300px; overflow-y: auto; color: #E5E7EB; border-left: 3px solid #6366F1;">{full_text}</div>', unsafe_allow_html=True)
                
                # Show key metadata if available
                if metadata:
                    st.markdown("**📊 Key Metrics:**")
                    cols = st.columns(3)
                    with cols[0]:
                        if "AMT_INCOME_TOTAL" in metadata:
                            st.metric("Income", f"${metadata['AMT_INCOME_TOTAL']:,.0f}")
                    with cols[1]:
                        if "AMT_CREDIT" in metadata:
                            st.metric("Credit Amount", f"${metadata['AMT_CREDIT']:,.0f}")
                    with cols[2]:
                        if "AMT_ANNUITY" in metadata:
                            st.metric("Annuity", f"${metadata['AMT_ANNUITY']:,.0f}")
    else:
        # No similar cases found
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📚</div>
            <p><small>No similar cases found in the database. This may be a unique profile or hypothetical scenario.</small></p>
        </div>
        """, unsafe_allow_html=True)


def render_shadow_analysis(num_similar_cases, decision_context, query):
    """Render shadow decision analysis results"""
    st.markdown('<div class="section-header">🔮 Shadow Decision Alternatives</div>', 
                unsafe_allow_html=True)
    
    # Get API client
    api = get_api_client()
    
    # Prepare alternatives for analysis
    alternatives = [
        {"name": "APPROVE", "description": "Full approval of the application"},
        {"name": "CONDITIONAL_APPROVE", "description": "Approval with conditions and monitoring"},
        {"name": "REJECT", "description": "Rejection of the application"},
        {"name": "DEFER", "description": "Defer decision pending additional information"}
    ]
    
    # Call API for complete analysis
    with st.spinner("Generating shadow decisions and analyzing alternatives..."):
        try:
            analysis_result = api.analyze_complete(
                decision_context=decision_context,
                query=query,
                alternatives=alternatives,
                top_k=num_similar_cases
            )
        except Exception as e:
            st.error(f"Error calling API: {str(e)}")
            analysis_result = None
    
    # Also fetch similar cases directly for display
    similar_cases_data = None
    try:
        search_result = api.search_text(query=query, top_k=num_similar_cases, use_llm=True)
        if search_result and search_result.get("results"):
            similar_cases_data = search_result["results"]
            st.session_state.last_similar_cases = similar_cases_data
    except Exception as e:
        st.warning(f"Could not fetch similar cases: {str(e)}")
    
    if not analysis_result:
        st.error("Failed to get analysis from API. Please try again.")
        return
    
    st.session_state.last_analysis = analysis_result
    
    # Extract risk analysis from agent
    risk_analysis = analysis_result.get("risk_analysis", {})
    structured_output = risk_analysis.get("structured_output", {})
    
    # Extract alternatives from structured output
    alternatives_analysis = structured_output.get("alternatives_risk_analysis", [])
    
    # Map alternatives to shadow format
    shadows = []
    mitigation_strategies = {m.get("alternative_id"): m for m in structured_output.get("mitigation_strategies", [])}
    
    if alternatives_analysis:
        for alt in alternatives_analysis:
            alt_id = alt.get("alternative_id", "")
            shadows.append({
                "decision": alt.get("alternative_description", alt_id).upper(),
                "risk_score": alt.get("risk_score", "N/A"),
                "default_probability": f"{alt.get('default_probability', 0):.1%}" if isinstance(alt.get('default_probability'), (int, float)) else "N/A",
                "risk": alt.get("risk_level", "Medium"),
                "cases": analysis_result.get("similar_cases_count", num_similar_cases),
                "risk_factors": alt.get("risk_factors", []),
                "analysis_text": alt.get("alternative_description", ""),
                "mitigation_strategy": mitigation_strategies.get(alt_id, {}).get("strategy", "")
            })
    
    # If no alternatives from agent, show error
    if not shadows:
        st.error("No alternatives were generated by the Risk Agent. The agent may not have returned structured output.")
        st.expander("🔍 Debug: View Raw Agent Output").write(risk_analysis.get("raw_output", "No output available"))
        return
    
    # Show analysis summary
    risk_comparison = structured_output.get("risk_comparison", {})
    if risk_comparison:
        recommendation = risk_comparison.get("recommendation", "")
        
        # Extract the recommended alternative from the recommendation text
        recommended_alt = None
        if "APPROVE" in recommendation.upper() and "CONDITIONAL" not in recommendation.upper():
            recommended_alt = "APPROVE"
        elif "CONDITIONAL" in recommendation.upper():
            recommended_alt = "CONDITIONAL_APPROVE"
        elif "REJECT" in recommendation.upper():
            recommended_alt = "REJECT"
        elif "DEFER" in recommendation.upper():
            recommended_alt = "DEFER"
        
        # Show agent's recommendation prominently with color coding
        if recommendation:
            if recommended_alt == "APPROVE":
                st.success(f"**🎯 Agent Recommendation:** {recommendation}")
                st.info("💰 **Business Impact:** Approving this loan is expected to be profitable with acceptable risk.")
            elif recommended_alt == "CONDITIONAL_APPROVE":
                st.warning(f"**🎯 Agent Recommendation:** {recommendation}")
                st.info("⚖️ **Business Impact:** Conditional approval balances profit potential with risk mitigation.")
            elif recommended_alt == "REJECT":
                st.error(f"**🎯 Agent Recommendation:** {recommendation}")
                st.warning("⚠️ **Business Impact:** Rejection avoids potential default but means zero revenue from this opportunity.")
            else:
                st.info(f"**🎯 Agent Recommendation:** {recommendation}")
        
        # Show summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Similar Cases Analyzed", analysis_result.get("similar_cases_count", 0))
        with col2:
            avg_sim = analysis_result.get('avg_similarity', 0)
            st.metric("Average Similarity", f"{avg_sim:.1%}")
    
    st.success(f"✓ Analysis complete | {len(shadows)} alternatives analyzed | Avg Similarity: {analysis_result.get('avg_similarity', 0):.2%}")
    
    # Create tabs for each alternative
    tab_labels = [f"{s['decision'][:15]}..." if len(s['decision']) > 15 else s['decision'] for s in shadows]
    tabs = st.tabs(tab_labels)
    
    for idx, tab in enumerate(tabs):
        with tab:
            render_shadow_decision_tab(shadows[idx], f"alt_{idx}")
    
    render_similar_cases(num_similar_cases, similar_cases_data)


def render_main_content(num_similar_cases, client_profile):
    """Render complete main content area"""
    
    # Mode selector
    mode = st.radio(
        "Select Mode",
        ["🔍 Search Clients", "⚖️ Decision Analysis"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if mode == "🔍 Search Clients":
        # Search mode
        st.markdown('<div class="section-header" style="color: #BACEFF;">🔍 Search Similar Clients</div>', 
                    unsafe_allow_html=True)
        
        search_query = st.text_area(
            "Search Query",
            placeholder="e.g., 'High income earners over 300k with stable employment' or 'Clients with good credit history'",
            height=80,
            key="search_input"
        )
        
        col_search, col_clear = st.columns([3, 1])
        with col_search:
            search_btn = st.button("🔍 Search", use_container_width=True, type="primary")
        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if search_btn and search_query:
            api = get_api_client()
            with st.spinner("Searching for similar clients..."):
                try:
                    search_result = api.search_text(query=search_query, top_k=num_similar_cases, use_llm=True)
                    if search_result and search_result.get("results"):
                        similar_cases_data = search_result["results"]
                        st.success(f"✓ Found {len(similar_cases_data)} matching clients")
                        
                        # Show query understanding if available
                        understanding = search_result.get("understanding")
                        if understanding:
                            with st.expander("🧠 Query Understanding"):
                                st.json(understanding)
                        
                        render_similar_cases(num_similar_cases, similar_cases_data)
                    else:
                        st.warning("No matching clients found")
                except Exception as e:
                    st.error(f"Search failed: {str(e)}")
        elif search_query and not search_btn:
            st.info("Click 'Search' to find similar clients")
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <p><small>Enter a search query to find similar clients in the database</small></p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Decision analysis mode
        st.markdown('<div class="section-header" style="color: #BACEFF;">⚖️ Generate Shadow Decisions</div>', 
                    unsafe_allow_html=True)
        
        # Initialize last_query if not exists
        if 'last_query' not in st.session_state:
            st.session_state.last_query = ""
        
        decision_context = st.text_area(
            "Decision Context",
            placeholder="Describe the decision to analyze (e.g., 'Should I approve a $50k loan for Client 100021?')",
            height=80,
            label_visibility="collapsed",
            key="decision_input",
            value=st.session_state.last_query
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
                st.session_state.last_analysis = None
                st.rerun()
        
        render_decision_templates()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if analyze_btn and decision_context:
            st.session_state.query_count += 1
            st.session_state.last_query = decision_context
            
            # Try to extract client ID from decision context
            import re
            client_id_match = re.search(r'\b(?:client|Client ID|ID)\s*[:#]?\s*(\d+)', decision_context)
            extracted_client_id = None
            if client_id_match:
                extracted_client_id = int(client_id_match.group(1))
            
            # Build comprehensive decision context including full client profile
            profile_text = ""
            current_client_id = None
            metadata = {}
            
            # ONLY use loaded profile if client ID is explicitly mentioned
            if extracted_client_id and st.session_state.get("current_profile"):
                current_profile = st.session_state.current_profile
                # Verify the loaded profile matches the mentioned client ID
                if current_profile.get("client_id") == extracted_client_id:
                    profile_text = current_profile.get("text", "")
                    current_client_id = current_profile.get("client_id")
                    metadata = current_profile.get("metadata", {})
            
            # If client ID mentioned but profile not loaded/mismatched, auto-fetch it
            if extracted_client_id and not current_client_id:
                api = get_api_client()
                with st.spinner(f"Fetching profile for Client {extracted_client_id}..."):
                    try:
                        profile_data = api.get_profile(extracted_client_id)
                        if profile_data and profile_data.get("client_id"):
                            st.success(f"✓ Auto-loaded profile for Client {extracted_client_id}")
                            st.session_state.current_client_id = extracted_client_id
                            st.session_state.current_profile = profile_data
                            profile_text = profile_data.get("text", "")
                            current_client_id = extracted_client_id
                            metadata = profile_data.get("metadata", {})
                        else:
                            st.warning(f"Could not find Client {extracted_client_id}. Analysis will proceed without profile data.")
                    except Exception as e:
                        st.warning(f"Failed to fetch Client {extracted_client_id}: {str(e)}. Analysis will proceed without profile data.")
            elif not extracted_client_id:
                st.info("📝 Analyzing hypothetical scenario (no client ID detected). For real client analysis, mention 'Client XXXXXX'.")
            
            # Create detailed decision context with FULL profile
            decision_ctx = {
                "client_id": current_client_id or client_profile.get("client_id"),
                "decision_type": "credit_application",
                "description": f"{decision_context}\n\n{'='*60}\nCLIENT FULL PROFILE:\n{'='*60}\n{profile_text}" if profile_text else decision_context,
                "additional_info": {
                    "age": client_profile.get("age"),
                    "income": client_profile.get("income"),
                    "education": client_profile.get("education"),
                    "employment": client_profile.get("employment"),
                    "profile_loaded": bool(profile_text)
                }
            }
            
            # Create focused search query with key details only (not full profile)
            enhanced_query = decision_context
            if profile_text and metadata:
                # Extract key financial metrics for better search matching
                key_details = []
                if metadata.get("AMT_INCOME_TOTAL"):
                    key_details.append(f"Income: ${metadata['AMT_INCOME_TOTAL']:,.0f}")
                if metadata.get("AMT_CREDIT"):
                    key_details.append(f"Credit: ${metadata['AMT_CREDIT']:,.0f}")
                if metadata.get("NAME_EDUCATION_TYPE"):
                    key_details.append(f"Education: {metadata['NAME_EDUCATION_TYPE']}")
                if metadata.get("NAME_INCOME_TYPE"):
                    key_details.append(f"Employment: {metadata['NAME_INCOME_TYPE']}")
                if metadata.get("CNT_CHILDREN") is not None:
                    key_details.append(f"Children: {metadata['CNT_CHILDREN']}")
                
                # Add payment history info if available
                if "AMT_CREDIT_SUM_DEBT" in metadata:
                    key_details.append(f"Current Debt: ${metadata['AMT_CREDIT_SUM_DEBT']:,.0f}")
                
                enhanced_query = f"{decision_context}\n\nKey Client Details:\n" + ", ".join(key_details)
            elif profile_text:
                # Fallback: use first 500 chars if no metadata
                enhanced_query = f"{decision_context}\n\n{profile_text[:500]}"
            
            render_shadow_analysis(num_similar_cases, decision_ctx, enhanced_query)
        
        elif decision_context and not analyze_btn:
            st.info("Click 'Analyze & Generate Shadows' to run the analysis")
        
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">⚖️</div>
                <p><small>Enter a specific decision context to analyze alternatives (e.g., loan approval decision)</small></p>
            </div>
            """, unsafe_allow_html=True)
