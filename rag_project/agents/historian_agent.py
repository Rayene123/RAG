"""
Historian Agent - Analyzes past decision patterns
"""
from typing import Dict, List, Any
from agents.base_agent import BaseAgent


class HistorianAgent(BaseAgent):
    """
    Historian Agent analyzes historical decision patterns
    to identify trends, precedents, and similar cases
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """Initialize Historian Agent with lower temperature for factual analysis"""
        super().__init__(model_name, temperature)
        
        # Create analysis chain
        self.chain = self._create_chain(self._get_prompt_template())
    
    def _get_prompt_template(self) -> str:
        """Get prompt template for historical analysis"""
        return """You are a Historian Agent analyzing past financial decisions.

Current Decision Context:
{decision_context}

Similar Past Cases:
{similar_cases}

Task: Analyze the historical patterns and provide:
1. Common characteristics in similar past cases
2. Historical outcomes (success/failure patterns)
3. Key precedents that apply to this case
4. Notable differences from past cases
5. Historical risk indicators

Provide a structured analysis in JSON format:
{{
    "common_patterns": ["pattern1", "pattern2"],
    "historical_outcomes": {{"success_rate": 0.XX, "failure_rate": 0.XX}},
    "key_precedents": ["precedent1", "precedent2"],
    "notable_differences": ["difference1", "difference2"],
    "risk_indicators": ["indicator1", "indicator2"]
}}

Analysis:"""
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze historical patterns for the given decision context
        
        Args:
            context: Dictionary containing:
                - decision_context: Current decision information
                - similar_cases: List of similar past cases from RAG
        
        Returns:
            Dictionary with historical analysis results
        """
        decision_context = context.get('decision_context', '')
        similar_cases = context.get('similar_cases', [])
        
        # Format similar cases
        formatted_cases = self._format_similar_cases(similar_cases)
        
        # Run chain
        result = self.chain.invoke({
            'decision_context': decision_context,
            'similar_cases': formatted_cases
        })
        
        # Parse and structure results
        analysis = {
            'agent': 'Historian',
            'raw_output': result.get('text', ''),
            'similar_cases_count': len(similar_cases),
            'avg_similarity_score': self._calculate_avg_score(similar_cases)
        }
        
        return analysis
    
    def _calculate_avg_score(self, cases: List[Dict]) -> float:
        """Calculate average similarity score"""
        if not cases:
            return 0.0
        scores = [case.get('score', 0) for case in cases]
        return sum(scores) / len(scores)
    
    def analyze_analyst_patterns(self, analyst_id: str, decisions: List[Dict]) -> Dict[str, Any]:
        """
        Analyze decision patterns for a specific analyst
        
        Args:
            analyst_id: ID of the analyst
            decisions: List of past decisions made by this analyst
        
        Returns:
            Pattern analysis for the analyst
        """
        prompt = f"""Analyze the decision-making patterns of Analyst {analyst_id}.

Past Decisions:
{self._format_decisions(decisions)}

Identify:
1. Decision tendencies (approval rate, rejection rate)
2. Common criteria used
3. Risk tolerance level
4. Consistency in similar cases

Provide analysis:"""
        
        result = self.llm.invoke(prompt)
        
        return {
            'analyst_id': analyst_id,
            'pattern_analysis': result.content,
            'total_decisions': len(decisions)
        }
    
    def _format_decisions(self, decisions: List[Dict]) -> str:
        """Format decisions for analysis"""
        if not decisions:
            return "No decisions available"
        
        formatted = []
        for i, dec in enumerate(decisions[:10], 1):  # Limit to 10 for context
            formatted.append(
                f"{i}. Decision: {dec.get('decision', 'N/A')} | "
                f"Client: {dec.get('client_id', 'N/A')} | "
                f"Outcome: {dec.get('outcome', 'N/A')}"
            )
        
        if len(decisions) > 10:
            formatted.append(f"... and {len(decisions) - 10} more decisions")
        
        return "\n".join(formatted)


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
    historian = HistorianAgent()
    
    # Real query to Qdrant
    query = "35-year-old client, $50k income, owns property, requesting $150k loan"
    similar_cases = retriever.search(query, top_k=5)
    
    # Analyze with real data
    context = {
        'decision_context': query,
        'similar_cases': similar_cases
    }
    
    result = historian.analyze(context)
    print("\n=== Historian Analysis ===")
    print(f"Similar cases found: {result['similar_cases_count']}")
    print(f"Average similarity: {result['avg_similarity_score']:.3f}")
    print(f"\nAnalysis:\n{result['raw_output']}")
