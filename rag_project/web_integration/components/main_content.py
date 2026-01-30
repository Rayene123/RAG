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
                st.session_state.decision_input = template_text  # Update textarea directly via its key
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
    
    # Check if we need to analyze uploaded PDF content
    if st.session_state.get("analyze_pdf_trigger") and st.session_state.get("analyze_pdf_file"):
        pdf_file = st.session_state.analyze_pdf_file
        
        st.markdown('<div class="section-header" style="color: #BACEFF;">📄 PDF Document Analysis</div>', 
                    unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <div style="font-size: 16px; font-weight: 600;">📄 {pdf_file.name}</div>
            <div style="color: #9CA3AF; font-size: 13px; margin-top: 5px;">Size: {pdf_file.size / 1024:.1f} KB</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("Analyzing PDF content..."):
            try:
                api = get_api_client()
                import sys
                import os
                
                # Add parent directory to path to import rag_core
                parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                # Extract text from PDF
                import tempfile
                
                # Save PDF temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_file.seek(0)
                    tmp_file.write(pdf_file.read())
                    tmp_path = tmp_file.name
                
                # Extract text using the PDF transformer
                from rag_core.query_processor.transformers.pdf_transformer import PDFTransformer
                pdf_transformer = PDFTransformer()
                
                # Transform returns a list of dictionaries with text and metadata
                extracted_data = pdf_transformer.transform(tmp_path)
                
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                
                if extracted_data:
                    # Get all text from all pages
                    all_text = ""
                    total_pages = 0
                    
                    # The transformer might return multiple entries or a single entry with all text
                    for data_item in extracted_data:
                        if 'text' in data_item:
                            all_text += data_item['text'] + "\n"
                            total_pages = max(total_pages, data_item.get('pages', 1))
                    
                    # If no text collected, try first item directly
                    if not all_text and extracted_data[0].get('text'):
                        all_text = extracted_data[0]['text']
                        total_pages = extracted_data[0].get('pages', 1)
                    
                    extracted_text = all_text.strip()
                    pages_extracted = total_pages
                    
                    if not extracted_text:
                        st.error("Failed to extract text from PDF")
                        return
                    
                    st.success(f"✓ Successfully extracted text from {pages_extracted} page(s) ({len(extracted_text)} characters)")
                    
                    # Display extracted text
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="section-header">📝 Extracted Content</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: #1E1E1E; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="color: #9CA3AF; font-size: 13px;">
                            📊 Total characters: {len(extracted_text):,} | Words: {len(extracted_text.split()):,} | Pages: {pages_extracted}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("View Full Text", expanded=True):
                        st.text_area("Document Text", extracted_text, height=300, key="pdf_text_display")
                    
                    # Generate comprehensive AI analysis
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="section-header">🤖 Comprehensive AI Analysis</div>', unsafe_allow_html=True)
                    
                    with st.spinner("Running full analysis with AI agents..."):
                        try:
                            api = get_api_client()
                            
                            # First, search for similar cases based on the document
                            search_result = api.search_text(query=extracted_text[:2000], top_k=5, use_llm=True)
                            
                            # Display similar cases found
                            st.markdown("### 📚 Similar Cases Found")
                            similar_cases_exist = search_result.get("results") and len(search_result["results"]) > 0
                            
                            if similar_cases_exist:
                                similar_count = len(search_result["results"])
                                st.success(f"Found {similar_count} similar profiles based on document content")
                                
                                # Show quick summary
                                outcomes = [r.get("target", 0) for r in search_result["results"]]
                                good_count = outcomes.count(0)
                                default_count = len(outcomes) - good_count
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Similar Cases", similar_count)
                                with col2:
                                    st.metric("Good Standing", f"{good_count} ({good_count/similar_count*100:.0f}%)")
                                with col3:
                                    st.metric("Default/Risk", f"{default_count} ({default_count/similar_count*100:.0f}%)")
                                
                                # Display similar cases
                                render_similar_cases(similar_count, search_result["results"])
                            else:
                                st.info("No similar cases found in database - analyzing document independently")
                            
                            # Run agent analysis regardless of similar cases
                            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                            st.markdown("### 🤖 AI Agent Analysis")
                            
                            # Run historical analysis
                            with st.spinner("Running Historian Agent..."):
                                try:
                                    hist_result = api.analyze_historical(
                                        decision_context={
                                            "client_id": None,
                                            "decision_type": "profile_evaluation",
                                            "description": f"Evaluate client profile from uploaded document. Document contains: {extracted_text[:800]}"
                                        },
                                        query=extracted_text,
                                        top_k=5
                                    )
                                    
                                    if hist_result:
                                        st.markdown("**📊 Historical Pattern Analysis:**")
                                        
                                        # Try to extract structured output - it might be directly in the result or nested
                                        structured_data = None
                                        
                                        # Check if structured_output exists at top level
                                        if 'structured_output' in hist_result:
                                            structured_data = hist_result['structured_output']
                                        # Otherwise try to parse raw_output JSON
                                        elif 'raw_output' in hist_result:
                                            import json
                                            import re
                                            raw = hist_result['raw_output']
                                            # Extract JSON from markdown code blocks
                                            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw, re.DOTALL)
                                            if json_match:
                                                try:
                                                    structured_data = json.loads(json_match.group(1))
                                                except:
                                                    pass
                                        
                                        if structured_data and isinstance(structured_data, dict):
                                            # Display common patterns
                                            if structured_data.get('common_patterns'):
                                                st.markdown("**Common Patterns Identified:**")
                                                for pattern in structured_data['common_patterns']:
                                                    st.markdown(f"- {pattern}")
                                            
                                            # Display historical outcomes
                                            if structured_data.get('historical_outcomes'):
                                                outcomes = structured_data['historical_outcomes']
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    success_rate = outcomes.get('success_rate', 0) * 100
                                                    st.metric("Success Rate", f"{success_rate:.0f}%")
                                                with col2:
                                                    failure_rate = outcomes.get('failure_rate', 0) * 100
                                                    st.metric("Failure Rate", f"{failure_rate:.0f}%")
                                            
                                            # Display key precedents
                                            if structured_data.get('key_precedents'):
                                                st.markdown("**Key Precedents:**")
                                                for precedent in structured_data['key_precedents']:
                                                    st.info(precedent)
                                            
                                            # Display risk indicators
                                            if structured_data.get('risk_indicators'):
                                                st.markdown("**⚠️ Risk Indicators:**")
                                                for indicator in structured_data['risk_indicators']:
                                                    st.markdown(f"- ⚠️ {indicator}")
                                        else:
                                            # Fallback to raw analysis text
                                            analysis_text = hist_result.get('analysis', hist_result.get('pattern_analysis', str(hist_result)))
                                            st.markdown(f"""
                                            <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #10b981;">
                                                <div style="color: #E5E7EB; font-size: 14px; line-height: 1.8; white-space: pre-wrap;">{analysis_text}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.warning("Historian agent did not return analysis")
                                except Exception as e:
                                    st.error(f"Historian analysis failed: {str(e)}")
                            
                            # Run risk analysis
                            with st.spinner("Running Risk Agent..."):
                                try:
                                    risk_result = api.analyze_risk(
                                        decision_context={
                                            "client_id": None,
                                            "decision_type": "profile_evaluation",
                                            "description": f"Assess risk for client profile. Full document: {extracted_text}"
                                        },
                                        query=extracted_text,
                                        alternatives=[
                                            {"name": "APPROVE", "description": "Approve this profile based on analysis"},
                                            {"name": "REJECT", "description": "Reject this profile due to risk factors"},
                                            {"name": "CONDITIONAL", "description": "Approve with conditions and monitoring"},
                                            {"name": "DEFER", "description": "Defer decision pending additional information"}
                                        ],
                                        top_k=5
                                    )
                                    
                                    if risk_result:
                                        st.markdown("**⚠️ Risk Assessment:**")
                                        
                                        # Try to extract structured output
                                        structured_data = None
                                        
                                        # Check if structured_output exists at top level
                                        if 'structured_output' in risk_result:
                                            structured_data = risk_result['structured_output']
                                        # Otherwise try to parse raw_output JSON
                                        elif 'raw_output' in risk_result:
                                            import json
                                            import re
                                            raw = risk_result['raw_output']
                                            # Extract JSON from markdown code blocks
                                            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw, re.DOTALL)
                                            if json_match:
                                                try:
                                                    structured_data = json.loads(json_match.group(1))
                                                except:
                                                    pass
                                        
                                        # Check for analysis text first (simple summary)
                                        if risk_result.get('analysis') and isinstance(risk_result['analysis'], str):
                                            st.markdown(f"""
                                            <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ef4444;">
                                                <div style="color: #E5E7EB; font-size: 14px; line-height: 1.8;">{risk_result['analysis']}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        
                                        if structured_data and isinstance(structured_data, dict):
                                            # Display overall risk summary
                                            if structured_data.get('overall_risk_summary'):
                                                st.markdown(f"""
                                                <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ef4444;">
                                                    <div style="color: #E5E7EB; font-size: 14px; line-height: 1.8;">{structured_data['overall_risk_summary']}</div>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            
                                            # Display decision alternatives with proper formatting
                                            if structured_data.get('alternatives_risk_analysis'):
                                                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                                                st.markdown("### 🎯 Decision Alternatives Analysis")
                                                
                                                alternatives = structured_data['alternatives_risk_analysis']
                                                
                                                for alt in alternatives:
                                                    alt_id = alt.get('alternative_id', 'Unknown')
                                                    risk_score = alt.get('risk_score', 'N/A')
                                                    risk_level = alt.get('risk_level', 'Unknown')
                                                    default_prob = alt.get('default_probability', 0) * 100
                                                    
                                                    # Color based on risk level
                                                    if risk_level == 'HIGH':
                                                        color = '#ef4444'
                                                    elif risk_level == 'MEDIUM':
                                                        color = '#f59e0b'
                                                    else:
                                                        color = '#10b981'
                                                    
                                                    with st.expander(f"**{alt_id}** - Risk: {risk_score}/10 ({risk_level})", expanded=False):
                                                        st.markdown(f"**Default Probability:** {default_prob:.1f}%")
                                                        
                                                        if alt.get('risk_factors'):
                                                            st.markdown("**Risk Factors:**")
                                                            for factor in alt['risk_factors']:
                                                                st.markdown(f"- ⚠️ {factor}")
                                            
                                            # Display risk comparison
                                            if structured_data.get('risk_comparison'):
                                                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                                                st.markdown("### 📊 Risk Comparison")
                                                comparison = structured_data['risk_comparison']
                                                
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    st.metric("Lowest Risk", comparison.get('lowest_risk_alternative', 'N/A'))
                                                with col2:
                                                    st.metric("Highest Risk", comparison.get('highest_risk_alternative', 'N/A'))
                                                with col3:
                                                    st.metric("Risk Spread", f"{comparison.get('risk_spread', 0)}")
                                                
                                                if comparison.get('recommendation'):
                                                    st.success(f"**Recommendation:** {comparison['recommendation']}")
                                            
                                            # Display mitigation strategies
                                            if structured_data.get('mitigation_strategies'):
                                                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                                                st.markdown("### 🛡️ Risk Mitigation Strategies")
                                                
                                                for strategy in structured_data['mitigation_strategies']:
                                                    with st.expander(f"{strategy.get('alternative_id', 'Strategy')} - {strategy.get('risk_factor', 'Risk Factor')}"):
                                                        st.markdown(f"**Strategy:** {strategy.get('strategy', 'N/A')}")
                                                        st.markdown(f"**Expected Impact:** {strategy.get('expected_impact', 'N/A')}")
                                        else:
                                            # Fallback to raw text
                                            risk_analysis_text = risk_result.get('analysis', risk_result.get('risk_assessment', str(risk_result)))
                                            st.markdown(f"""
                                            <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ef4444;">
                                                <div style="color: #E5E7EB; font-size: 14px; line-height: 1.8; white-space: pre-wrap;">{risk_analysis_text}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.warning("Risk agent did not return analysis")
                                except Exception as e:
                                    st.error(f"Risk analysis failed: {str(e)}")
                                    
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
                            import traceback
                            with st.expander("Error Details"):
                                st.code(traceback.format_exc())
                        
                        # Fallback: Show basic statistics
                    
                    # Find similar cases based on PDF content
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="section-header">🔍 Similar Cases Found</div>', unsafe_allow_html=True)
                    
                    pdf_search_results = st.session_state.get("pdf_search_results", [])
                    if pdf_search_results:
                        render_similar_cases(len(pdf_search_results), pdf_search_results)
                    else:
                        st.info("Click 'Search' button to find similar clients")
                    
                else:
                    st.error("Failed to extract text from PDF")
                    
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
        
        # Back button
        if st.button("← Back to Upload"):
            st.session_state.analyze_pdf_trigger = False
            st.session_state.analyze_pdf_file = None
            st.rerun()
        
        return
    
    # Check if we need to analyze a client from PDF/image search
    if st.session_state.get("analyze_trigger") and st.session_state.get("analyze_client_id"):
        client_id = st.session_state.analyze_client_id
        
        st.markdown('<div class="section-header" style="color: #BACEFF;">📊 Client Analysis</div>', 
                    unsafe_allow_html=True)
        
        with st.spinner(f"Running complete analysis for Client {client_id}..."):
            try:
                api = get_api_client()
                
                # Get analyzed profile with similar cases and AI insights
                analysis = api.get_analyzed_profile(client_id)
                
                if analysis:
                    st.success(f"✓ Analysis complete for Client {client_id}")
                    
                    # Display client profile
                    profile = analysis.get("profile", {})
                    if profile:
                        target = profile.get("target", 0)
                        outcome_color = "#16a34a" if target == 0 else "#dc2626"
                        outcome_text = "Good Standing" if target == 0 else "Default/Rejected"
                        
                        st.markdown(f"""
                        <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">Client {client_id}</div>
                            <div style="color: {outcome_color}; font-weight: 500;">Status: {outcome_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        profile_text = profile.get("text", "No description available")
                        st.markdown("**📄 Profile:**")
                        st.markdown(f'<div style="background: #0D1117; padding: 15px; border-radius: 8px; font-size: 13px; line-height: 1.6; max-height: 200px; overflow-y: auto; color: #E5E7EB; border-left: 3px solid #6366F1;">{profile_text}</div>', unsafe_allow_html=True)
                    
                    # Display similar cases
                    similar_cases = analysis.get("similar_cases", [])
                    if similar_cases:
                        render_similar_cases(len(similar_cases), similar_cases)
                    
                    # Display AI analysis if available
                    if analysis.get("historical_analysis"):
                        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                        st.markdown('<div class="section-header">🤖 AI Analysis</div>', unsafe_allow_html=True)
                        st.info(analysis["historical_analysis"])
                    
                    # Store in session
                    st.session_state.last_analysis = analysis
                else:
                    st.error("Failed to retrieve analysis")
                    
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
        
        # Clear the trigger
        if st.button("Back to Search"):
            st.session_state.analyze_trigger = False
            st.session_state.analyze_client_id = None
            st.rerun()
        
        return
    
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
        
        # Display selected client profile if one is selected
        if st.session_state.get("current_profile"):
            profile = st.session_state.current_profile
            client_id = profile.get("client_id", "Unknown")
            target = profile.get("target", 0)
            outcome_color = "#16a34a" if target == 0 else "#dc2626"
            outcome_text = "Good Standing" if target == 0 else "Default/Rejected"
            
            with st.expander(f"📋 Selected Client: {client_id}", expanded=True):
                st.markdown(f"""
                <div style="background: #1E1E1E; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 10px;">Client {client_id}</div>
                    <div style="color: {outcome_color}; font-weight: 500; margin-bottom: 15px;">Status: {outcome_text}</div>
                """, unsafe_allow_html=True)
                
                # Display profile text
                profile_text = profile.get("text", "No description available")
                st.markdown("**📄 Profile Details:**")
                st.markdown(f'<div style="background: #0D1117; padding: 15px; border-radius: 8px; font-size: 13px; line-height: 1.6; max-height: 250px; overflow-y: auto; color: #E5E7EB; border-left: 3px solid #6366F1;">{profile_text}</div>', unsafe_allow_html=True)
                
                # Display metadata if available
                metadata = profile.get("metadata", {})
                if metadata:
                    st.markdown("**📊 Key Metrics:**")
                    cols = st.columns(4)
                    metric_idx = 0
                    key_metrics = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "DAYS_EMPLOYED"]
                    for key in key_metrics:
                        if key in metadata and metadata[key] is not None:
                            with cols[metric_idx % 4]:
                                label = key.replace("AMT_", "").replace("DAYS_", "").replace("_", " ").title()
                                value = metadata[key]
                                if "AMT" in key:
                                    st.metric(label, f"${value:,.0f}")
                                else:
                                    st.metric(label, f"{abs(int(value))} days")
                            metric_idx += 1
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Clear button
                if st.button("Clear Selection", key="clear_profile"):
                    st.session_state.current_profile = None
                    st.session_state.current_client_id = None
                    st.rerun()
        
        search_query = st.text_area(
            "Search Query",
            placeholder="e.g., 'High income earners over 300k with stable employment' or 'Clients with good credit history'",
            height=80,
            key="search_input"
        )
        
        # Show active filters if any
        active_filters = []
        if st.session_state.get("filter_age_min") is not None:
            active_filters.append(f"Age: {st.session_state.filter_age_min}-{st.session_state.filter_age_max}")
        if st.session_state.get("filter_income_min") is not None:
            active_filters.append(f"Income: ${st.session_state.filter_income_min:,}-${st.session_state.filter_income_max:,}")
        if st.session_state.get("filter_target") is not None:
            outcome = "Good Standing" if st.session_state.filter_target == 0 else "Default/Risk"
            active_filters.append(f"Outcome: {outcome}")
        
        if active_filters:
            st.info(f"🔍 Active filters: {', '.join(active_filters)}")
        
        col_search, col_clear = st.columns([3, 1])
        with col_search:
            search_btn = st.button("🔍 Search", use_container_width=True, type="primary")
        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if search_btn and (search_query or active_filters):
            api = get_api_client()
            
            # Build filter dict from session state
            filters = {}
            if st.session_state.get("filter_age_min") is not None:
                filters["DAYS_BIRTH"] = {
                    "gte": -(st.session_state.filter_age_max * 365),  # Qdrant uses negative days
                    "lte": -(st.session_state.filter_age_min * 365)
                }
            if st.session_state.get("filter_income_min") is not None:
                filters["AMT_INCOME_TOTAL"] = {
                    "gte": st.session_state.filter_income_min,
                    "lte": st.session_state.filter_income_max
                }
            if st.session_state.get("filter_target") is not None:
                filters["TARGET"] = st.session_state.filter_target
            
            with st.spinner("Searching for similar clients..."):
                try:
                    if filters and search_query:
                        # Use hybrid search with both query and filters
                        search_result = api.search_hybrid(query=search_query, filters=filters, top_k=num_similar_cases)
                    elif filters:
                        # Use metadata search only
                        search_result = api.search_metadata(filters=filters, top_k=num_similar_cases)
                    else:
                        # Use text search only
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
        
        # Initialize decision_input in session state if not exists
        if 'decision_input' not in st.session_state:
            st.session_state.decision_input = ""
        
        # Render templates BEFORE the textarea so we can update session state
        render_decision_templates()
        
        decision_context = st.text_area(
            "Decision Context",
            placeholder="Describe the decision to analyze (e.g., 'Should I approve a $50k loan for Client 100021?')",
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
                st.session_state.decision_input = ""
                st.session_state.last_analysis = None
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if analyze_btn and decision_context:
            st.session_state.query_count += 1
            st.session_state.last_query = decision_context
            
            # Try to extract client ID from decision context
            import re
            client_id_match = re.search(r'\b(?:[Cc]lient|Client\s+ID|ID)\s*[:#]?\s*(\d+)', decision_context)
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
            
            # Detect if user mentioned a specific credit/loan amount in their query
            import re
            credit_match = re.search(r'\$\s*([\d,]+)k?\s*(loan|credit)', decision_context, re.IGNORECASE) or \
                          re.search(r'(loan|credit)\s*(of|for)?\s*\$\s*([\d,]+)k?', decision_context, re.IGNORECASE)
            
            new_credit_amount = None
            if credit_match:
                # Extract the amount
                amount_str = credit_match.group(1) if credit_match.group(1) else credit_match.group(3)
                amount_str = amount_str.replace(',', '')
                # Check if it's in "k" format (e.g., "50k")
                if 'k' in decision_context[credit_match.start():credit_match.end()].lower():
                    new_credit_amount = float(amount_str) * 1000
                else:
                    new_credit_amount = float(amount_str)
            
            # Create detailed decision context with emphasis on NEW credit amount if specified
            context_description = decision_context
            if profile_text:
                if new_credit_amount:
                    # Emphasize the NEW loan amount at the top
                    context_description = f"""{'='*60}
⚠️ NEW LOAN APPLICATION: ${new_credit_amount:,.0f}
{'='*60}

{decision_context}

{'='*60}
CLIENT HISTORICAL PROFILE (for reference only - amounts below are PAST data):
{'='*60}
{profile_text}"""
                else:
                    context_description = f"{decision_context}\n\n{'='*60}\nCLIENT FULL PROFILE:\n{'='*60}\n{profile_text}"
            
            # Create detailed decision context with FULL profile
            decision_ctx = {
                "client_id": current_client_id or client_profile.get("client_id"),
                "decision_type": "credit_application",
                "description": context_description,
                "additional_info": {
                    "age": client_profile.get("age"),
                    "income": client_profile.get("income"),
                    "education": client_profile.get("education"),
                    "employment": client_profile.get("employment"),
                    "profile_loaded": bool(profile_text),
                    "new_loan_amount": new_credit_amount
                }
            }
            
            # Create focused search query with key details only (not full profile)
            enhanced_query = decision_context
            if profile_text and metadata:
                # Extract key financial metrics for better search matching
                key_details = []
                if metadata.get("AMT_INCOME_TOTAL"):
                    key_details.append(f"Income: ${metadata['AMT_INCOME_TOTAL']:,.0f}")
                
                # Only include credit amount from profile if NOT mentioned in decision context
                if not new_credit_amount and metadata.get("AMT_CREDIT"):
                    key_details.append(f"Credit: ${metadata['AMT_CREDIT']:,.0f}")
                
                if metadata.get("NAME_EDUCATION_TYPE"):
                    key_details.append(f"Education: {metadata['NAME_EDUCATION_TYPE']}")
                if metadata.get("NAME_INCOME_TYPE"):
                    key_details.append(f"Employment: {metadata['NAME_INCOME_TYPE']}")
                if metadata.get("CNT_CHILDREN") is not None:
                    key_details.append(f"Children: {metadata['CNT_CHILDREN']}")
                
                # Add payment history info if available (only if credit not mentioned)
                if not new_credit_amount and "AMT_CREDIT_SUM_DEBT" in metadata:
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
