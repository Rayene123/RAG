"""
Risk Agent - Assesses risk for decision alternatives
"""
from typing import Dict, List, Any
import json
from agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    """
    Risk Agent assesses risk for each decision alternative,
    calculates default probabilities, compares risk across options,
    and provides mitigation strategies
    """
    
    def __init__(self, model_name: str = "mistral-small-latest", temperature: float = 0.2):
        """Initialize Risk Agent with very low temperature for consistent risk analysis"""
        super().__init__(model_name, temperature)
        
        # Create analysis chain
        self.chain = self._create_chain(self._get_prompt_template())
    
    def _get_prompt_template(self) -> str:
        """Get prompt template for risk analysis"""
        return """You are a Risk Agent analyzing financial decision alternatives.

Current Decision Context:
{decision_context}

Decision Alternatives:
{alternatives}

Similar Past Cases:
{similar_cases}

Task: Analyze each alternative and provide:
1. Risk assessment for each alternative (scale 1-10, where 10 is highest risk)
2. Default probability estimates (0.0 to 1.0)
3. Risk comparison across alternatives
4. Specific risk factors identified for each alternative
5. Mitigation strategies for top risks

Provide a structured analysis in JSON format:
{{
    "alternatives_risk_analysis": [
        {{
            "alternative_id": "alt_1",
            "alternative_description": "brief description",
            "risk_score": 7.5,
            "default_probability": 0.35,
            "risk_factors": ["factor1", "factor2", "factor3"],
            "risk_level": "HIGH|MEDIUM|LOW"
        }}
    ],
    "risk_comparison": {{
        "lowest_risk_alternative": "alt_id",
        "highest_risk_alternative": "alt_id",
        "risk_spread": 0.XX,
        "recommendation": "brief recommendation"
    }},
    "mitigation_strategies": [
        {{
            "alternative_id": "alt_1",
            "risk_factor": "specific risk",
            "strategy": "mitigation approach",
            "expected_impact": "HIGH|MEDIUM|LOW"
        }}
    ],
    "overall_risk_summary": "summary of key risk insights"
}}

Analysis:"""
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk for decision alternatives
        
        Args:
            context: Dictionary containing:
                - decision_context: Current decision information
                - alternatives: List of decision alternatives to evaluate
                - similar_cases: List of similar past cases from RAG
        
        Returns:
            Dictionary with risk analysis results
        """
        decision_context = context.get('decision_context', '')
        alternatives = context.get('alternatives', [])
        similar_cases = context.get('similar_cases', [])
        
        # Format inputs
        formatted_alternatives = self._format_alternatives(alternatives)
        formatted_cases = self._format_similar_cases(similar_cases)
        
        # Run chain (LCEL returns AIMessage, extract content)
        result = self.chain.invoke({
            'decision_context': decision_context,
            'alternatives': formatted_alternatives,
            'similar_cases': formatted_cases
        })
        
        # Parse and structure results
        analysis = {
            'agent': 'Risk',
            'raw_output': result.content if hasattr(result, 'content') else str(result),
            'alternatives_analyzed': len(alternatives),
            'similar_cases_count': len(similar_cases),
            'avg_similarity_score': self._calculate_avg_score(similar_cases),
            'historical_default_rate': self._calculate_historical_default_rate(similar_cases)
        }
        
        # Try to extract structured data from output
        try:
            analysis['structured_output'] = self._extract_json_from_output(analysis['raw_output'])
        except:
            analysis['structured_output'] = None
        
        return analysis
    
    def _format_alternatives(self, alternatives: List[Dict]) -> str:
        """Format decision alternatives for LLM consumption"""
        if not alternatives:
            return "No alternatives provided."
        
        formatted = []
        for i, alt in enumerate(alternatives, 1):
            alt_info = [
                f"═══ Alternative {i} ═══",
                f"ID: {alt.get('id', f'alt_{i}')}",
                f"Description: {alt.get('description', 'N/A')}"
            ]
            
            # Add all other fields
            for key, value in alt.items():
                if key not in ['id', 'description']:
                    alt_info.append(f"{key}: {value}")
            
            formatted.append("\n".join(alt_info))
        
        return "\n\n".join(formatted)
    
    def _calculate_avg_score(self, cases: List[Dict]) -> float:
        """Calculate average similarity score"""
        if not cases:
            return 0.0
        scores = [case.get('score', 0) for case in cases]
        return sum(scores) / len(scores)
    
    def _calculate_historical_default_rate(self, cases: List[Dict]) -> float:
        """Calculate default rate from similar historical cases"""
        if not cases:
            return 0.0
        
        defaults = 0
        total = 0
        
        for case in cases:
            # Check target in various locations
            target = case.get('target')
            if target is None:
                metadata = case.get('metadata', {})
                target = metadata.get('target')
            if target is None:
                payload = case.get('payload', {})
                target = payload.get('target')
            
            if target is not None:
                total += 1
                if target == 1:  # 1 typically indicates default
                    defaults += 1
        
        return defaults / total if total > 0 else 0.0
    
    def _extract_json_from_output(self, output: str) -> Dict:
        """Try to extract JSON from LLM output"""
        # Find JSON in output
        start = output.find('{')
        end = output.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = output[start:end]
            return json.loads(json_str)
        
        return None
    
    def assess_single_alternative(self, 
                                 alternative: Dict[str, Any],
                                 decision_context: Dict[str, Any],
                                 similar_cases: List[Dict]) -> Dict[str, Any]:
        """
        Assess risk for a single alternative
        
        Args:
            alternative: Single alternative to assess
            decision_context: Context information
            similar_cases: Similar historical cases
        
        Returns:
            Risk assessment for the alternative
        """
        context = {
            'decision_context': decision_context,
            'alternatives': [alternative],
            'similar_cases': similar_cases
        }
        
        return self.analyze(context)
    
    def compare_alternatives(self,
                           alternatives: List[Dict[str, Any]],
                           similar_cases: List[Dict]) -> Dict[str, Any]:
        """
        Compare risk across multiple alternatives
        
        Args:
            alternatives: List of alternatives to compare
            similar_cases: Historical cases for context
        
        Returns:
            Comparative risk analysis
        """
        prompt = f"""Compare the following alternatives from a risk perspective:

Alternatives:
{self._format_alternatives(alternatives)}

Historical Context:
- Historical default rate: {self._calculate_historical_default_rate(similar_cases):.2%}
- Similar cases analyzed: {len(similar_cases)}

Provide:
1. Risk ranking (lowest to highest risk)
2. Key risk differentiators
3. Recommended alternative from risk perspective
4. Trade-offs between alternatives

Analysis:"""
        
        result = self.llm.invoke(prompt)
        
        return {
            'comparison_analysis': result.content if hasattr(result, 'content') else str(result),
            'alternatives_compared': len(alternatives),
            'historical_context': {
                'default_rate': self._calculate_historical_default_rate(similar_cases),
                'cases_count': len(similar_cases)
            }
        }
    
    def generate_mitigation_strategies(self,
                                      risk_factors: List[str],
                                      alternative_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate specific mitigation strategies for identified risk factors
        
        Args:
            risk_factors: List of identified risk factors
            alternative_context: Context about the alternative
        
        Returns:
            List of mitigation strategies
        """
        prompt = f"""Generate specific mitigation strategies for the following risk factors:

Risk Factors:
{self._format_risk_factors(risk_factors)}

Alternative Context:
{self._format_context(alternative_context)}

For each risk factor, provide:
1. Specific mitigation action
2. Expected impact (HIGH/MEDIUM/LOW)
3. Implementation difficulty (EASY/MODERATE/HARD)
4. Timeline for implementation

Provide structured strategies:"""
        
        result = self.llm.invoke(prompt)
        
        strategies_text = result.content if hasattr(result, 'content') else str(result)
        
        return {
            'risk_factors': risk_factors,
            'mitigation_strategies': strategies_text,
            'factors_count': len(risk_factors)
        }
    
    def _format_risk_factors(self, factors: List[str]) -> str:
        """Format risk factors as numbered list"""
        if not factors:
            return "No risk factors provided"
        return "\n".join([f"{i}. {factor}" for i, factor in enumerate(factors, 1)])
    
    def _format_context(self, context: Dict) -> str:
        """Format context dictionary as string"""
        if not context:
            return "No context provided"
        return "\n".join([f"{key}: {value}" for key, value in context.items()])
    
    def analyze_from_text(self, 
                         client_description: str,
                         retriever=None) -> Dict[str, Any]:
        """
        SIMPLE INPUT: Just give a text description and get full counterfactual analysis!
        
        Args:
            client_description: Text like "35-year-old client, $60k income, requesting $150k loan"
            retriever: QdrantRetriever instance (optional, will create if not provided)
        
        Returns:
            Complete counterfactual analysis with recommendations
        
        Example:
            risk_agent = RiskAgent()
            result = risk_agent.analyze_from_text(
                "35-year-old tech worker, $90k income, requesting $150k loan"
            )
        """
        # Import retriever if needed
        if retriever is None:
            from rag_core.retriever.qdrant_retriever import QdrantRetriever
            retriever = QdrantRetriever()
        
        # Search for similar clients
        print(f"🔍 Searching for clients similar to: {client_description}")
        candidates = retriever.search(client_description, top_k=10)
        
        if not candidates:
            return {
                'error': 'No similar clients found in database',
                'query': client_description
            }
        
        # Get the most similar client
        best_match = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)[0]
        
        # Extract information from the best match
        client_id = best_match.get('client_id', 'N/A')
        client_text = best_match.get('text', '')
        similarity_score = best_match.get('score', 0)
        
        print(f"✓ Found most similar client: {client_id} (similarity: {similarity_score:.4f})")
        
        # Extract values from text using regex
        import re
        
        def extract_value(text, pattern, default=0):
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value_str = match.group(1).replace(',', '').replace('$', '').replace(' ', '').strip()
                try:
                    return float(value_str)
                except:
                    return default
            return default
        
        income = extract_value(client_text, r'(?:annual\s+)?income[:\s]+\$?([\d,]+)', 50000)
        credit = extract_value(client_text, r'(?:requested\s+)?credit(?:\s+amount)?[:\s]+\$?([\d,]+)', 80000)
        annuity = extract_value(client_text, r'(?:monthly\s+)?annuity[:\s]+\$?([\d,]+)', 0)
        
        # Get target (actual decision)
        target = best_match.get('target')
        if target is None:
            metadata = best_match.get('metadata', {}) or best_match.get('payload', {})
            target = metadata.get('target', 0)
        
        print(f"✓ Extracted: Income=${income:,.0f}, Credit=${credit:,.0f}, Decision={'REJECTED' if target == 1 else 'ACCEPTED'}")
        
        # Get similar cases (excluding the match itself)
        all_similar = retriever.search(client_text[:300] if client_text else client_description, top_k=15)
        similar_cases = [c for c in all_similar if c.get('client_id') != client_id][:10]
        
        print(f"✓ Found {len(similar_cases)} similar historical cases")
        
        # Build client profile
        client_profile = {
            'client_id': client_id,
            'client_text': client_text,
            'target': target,
            'income': income,
            'credit': credit,
            'annuity': annuity,
            'similarity_score': similarity_score
        }
        
        # Run counterfactual analysis
        print(f"📊 Running counterfactual analysis...")
        return self.analyze_counterfactual(client_profile, similar_cases)

    def analyze_counterfactual(self,
                              client_profile: Dict[str, Any],
                              similar_cases: List[Dict]) -> Dict[str, Any]:
        """
        Automatic counterfactual analysis: analyzes the actual decision and evaluates
        what would have happened with the opposite decision.
        
        Args:
            client_profile: Dictionary containing:
                - client_id: Client identifier
                - client_text: Full client profile text
                - target: Actual decision (0=ACCEPTED, 1=REJECTED/DEFAULT)
                - income: Annual income
                - credit: Requested credit amount
                - annuity: Monthly payment (optional)
            similar_cases: List of similar historical cases
        
        Returns:
            Dictionary with counterfactual analysis including percentage confidence
        """
        # Extract client info
        client_id = client_profile.get('client_id', 'N/A')
        target = client_profile.get('target', 0)
        income = client_profile.get('income', 0)
        credit = client_profile.get('credit', 0)
        annuity = client_profile.get('annuity', 0)
        
        # Calculate loan-to-income ratio
        loan_to_income_ratio = credit / income if income > 0 else 0
        
        # Calculate historical default rate
        default_rate = self._calculate_historical_default_rate(similar_cases)
        
        # Build context
        context = f"""
CLIENT PROFILE:
- Client ID: {client_id}
- Revenue: ${income:,.0f}
- Requested Credit: ${credit:,.0f}
- Loan-to-Income Ratio: {loan_to_income_ratio:.2f}

HISTORICAL CONTEXT:
- Similar Cases: {len(similar_cases)} clients found
- Average Similarity Score: {self._calculate_avg_score(similar_cases):.4f}
- Historical Default Rate: {default_rate:.2%}
- Actual Outcome: {"DEFAULT occurred" if target == 1 else "NO DEFAULT (good standing)"}

TASK: Perform counterfactual analysis comparing the actual decision vs the alternative decision.
For each alternative, provide:
1. Clear explanation of why the decision was made
2. For the counterfactual: percentage confidence (0-100%) that it would have been a better decision
3. Detailed reasoning based on client profile, historical data, and actual outcome

Respond in JSON format:
{{
    "actual_decision_analysis": {{
        "decision": "ACCEPTED" or "REJECTED",
        "justification": "Why this decision was made",
        "supporting_factors": ["list", "of", "factors"],
        "outcome": "What actually happened"
    }},
    "counterfactual_analysis": {{
        "alternative_decision": "REJECTED" or "ACCEPTED",
        "quality_score": 0-100 (percentage that alternative would have been better),
        "confidence_level": "HIGH/MEDIUM/LOW",
        "would_it_be_better": "YES/NO",
        "reasoning": "Detailed explanation",
        "risk_factors": ["factors supporting or against the alternative"],
        "conclusion": "Final verdict with percentage"
    }},
    "comparison_summary": "Overall comparison and recommendation"
}}
"""
        
        # Create alternatives automatically based on actual decision
        if target == 0:  # Client was ACCEPTED
            alternatives = [
                {
                    'id': 'actual_decision',
                    'description': f'DÉCISION RÉELLE: ACCEPTÉ - Crédit de ${credit:,.0f} accordé',
                    'loan_amount': credit,
                    'loan_to_income_ratio': loan_to_income_ratio,
                    'decision': 'ACCEPTED',
                    'outcome': 'NO_DEFAULT',
                    'analysis_request': 'Expliquer pourquoi cette décision était justifiée'
                },
                {
                    'id': 'counterfactual',
                    'description': f'ALTERNATIVE CONTREFACTUELLE: REJETER la demande',
                    'loan_amount': 0,
                    'decision': 'REJECTED',
                    'analysis_request': f'Si on avait REJETÉ: (1) Bonne ou mauvaise décision? (2) Pourcentage de certitude (0-100%). (3) Justification basée sur taux défaut ({default_rate:.1%}) et résultat (aucun défaut)'
                }
            ]
        else:  # Client was REJECTED (default observed)
            alternatives = [
                {
                    'id': 'actual_decision',
                    'description': f'DÉCISION RÉELLE: REJETÉ - Demande refusée',
                    'loan_amount': 0,
                    'decision': 'REJECTED',
                    'outcome': 'DEFAULT_OBSERVED',
                    'analysis_request': 'Expliquer pourquoi ce rejet était justifié'
                },
                {
                    'id': 'counterfactual',
                    'description': f'ALTERNATIVE CONTREFACTUELLE: ACCEPTER ${credit:,.0f}',
                    'loan_amount': credit,
                    'loan_to_income_ratio': loan_to_income_ratio,
                    'decision': 'ACCEPTED',
                    'analysis_request': f'Si on avait ACCEPTÉ: (1) Bonne ou mauvaise décision? (2) Pourcentage de certitude (0-100%). (3) Justification basée sur taux défaut ({default_rate:.1%}) et résultat (défaut observé)'
                }
            ]
        
        # Run analysis
        return self.analyze({
            'decision_context': context,
            'alternatives': alternatives,
            'similar_cases': similar_cases
        })

    def calculate_risk_metrics(self, similar_cases: List[Dict]) -> Dict[str, Any]:
        """
        Calculate various risk metrics from historical cases
        
        Args:
            similar_cases: List of similar historical cases
        
        Returns:
            Dictionary with risk metrics
        """
        if not similar_cases:
            return {
                'default_rate': 0.0,
                'cases_analyzed': 0,
                'confidence_level': 'VERY_LOW'
            }
        
        defaults = 0
        total = 0
        risk_scores = []
        
        for case in similar_cases:
            # Get target
            target = case.get('target')
            if target is None:
                metadata = case.get('metadata', {}) or case.get('payload', {})
                target = metadata.get('target')
            
            if target is not None:
                total += 1
                if target == 1:
                    defaults += 1
            
            # Get similarity score
            score = case.get('score', 0)
            risk_scores.append(score)
        
        default_rate = defaults / total if total > 0 else 0.0
        avg_similarity = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Determine confidence level
        if total >= 20 and avg_similarity > 0.7:
            confidence = 'HIGH'
        elif total >= 10 and avg_similarity > 0.5:
            confidence = 'MEDIUM'
        elif total >= 5:
            confidence = 'LOW'
        else:
            confidence = 'VERY_LOW'
        
        return {
            'default_rate': default_rate,
            'cases_analyzed': total,
            'avg_similarity': avg_similarity,
            'confidence_level': confidence,
            'risk_category': self._categorize_risk(default_rate)
        }
    
    def _categorize_risk(self, default_rate: float) -> str:
        """Categorize risk based on default rate"""
        if default_rate >= 0.5:
            return 'VERY_HIGH'
        elif default_rate >= 0.3:
            return 'HIGH'
        elif default_rate >= 0.15:
            return 'MEDIUM'
        elif default_rate >= 0.05:
            return 'LOW'
        else:
            return 'VERY_LOW'


# Example usage
if __name__ == "__main__":
    import sys
    import os
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    from rag_core.retriever.qdrant_retriever import QdrantRetriever
    
    # Initialize retriever and agent
    retriever = QdrantRetriever()
    risk_agent = RiskAgent()
    
    # Real query to Qdrant
    query = "45-year-old client, $40k income, owns property, requesting $100k loan"
    similar_cases = retriever.search(query, top_k=10)
    
    # Define decision alternatives
    alternatives = [
        {
            'id': 'alt_1',
            'description': 'Approve full loan amount ($100k) with standard interest rate (8%)',
            'loan_amount': 100000,
            'interest_rate': 0.08,
            'term_years': 30
        },
        {
            'id': 'alt_2',
            'description': 'Approve reduced loan amount ($75k) with lower interest rate (6.5%)',
            'loan_amount': 75000,
            'interest_rate': 0.065,
            'term_years': 30
        },
        {
            'id': 'alt_3',
            'description': 'Approve full loan with higher interest rate (10%) and co-signer requirement',
            'loan_amount': 100000,
            'interest_rate': 0.10,
            'term_years': 30,
            'requires_cosigner': True
        },
        {
            'id': 'alt_4',
            'description': 'Reject loan application',
            'loan_amount': 0,
            'decision': 'REJECT'
        }
    ]
    
    # Analyze with real data
    context = {
        'decision_context': query,
        'alternatives': alternatives,
        'similar_cases': similar_cases
    }
    
    result = risk_agent.analyze(context)
    print("\n" + "="*80)
    print("RISK AGENT ANALYSIS - REAL DATA FROM QDRANT")
    print("="*80)
    print(f"\n📊 Alternatives Analyzed: {result['alternatives_analyzed']}")
    print(f"📊 Retrieved Cases: {result['similar_cases_count']}")
    print(f"📈 Average Similarity Score: {result['avg_similarity_score']:.4f}")
    print(f"⚠️  Historical Default Rate: {result['historical_default_rate']:.2%}")
    
    # Show risk metrics
    print("\n" + "-"*80)
    print("RISK METRICS:")
    print("-"*80)
    metrics = risk_agent.calculate_risk_metrics(similar_cases)
    print(f"Default Rate: {metrics['default_rate']:.2%}")
    print(f"Cases Analyzed: {metrics['cases_analyzed']}")
    print(f"Average Similarity: {metrics['avg_similarity']:.4f}")
    print(f"Confidence Level: {metrics['confidence_level']}")
    print(f"Risk Category: {metrics['risk_category']}")
    
    print("\n" + "-"*80)
    print("AI RISK ANALYSIS:")
    print("-"*80)
    print(result['raw_output'])
    
    # Show structured output if available
    if result.get('structured_output'):
        print("\n" + "-"*80)
        print("STRUCTURED OUTPUT:")
        print("-"*80)
        print(json.dumps(result['structured_output'], indent=2))
    
    # Compare alternatives
    print("\n" + "="*80)
    print("ALTERNATIVE COMPARISON:")
    print("="*80)
    comparison = risk_agent.compare_alternatives(alternatives, similar_cases)
    print(comparison['comparison_analysis'])
