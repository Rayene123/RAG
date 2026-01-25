"""
Agent Orchestrator - Coordinates historian agent for decision analysis
"""
from typing import Dict, List, Any
from agents.historian_agent import HistorianAgent


class AgentOrchestrator:
    """
    Orchestrates the Historian agent for decision analysis
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize historian agent
        
        Args:
            model_name: LLM model to use
        """
        self.historian = HistorianAgent(model_name=model_name)
    
    def analyze_decision(self,
                        decision_context: Dict[str, Any],
                        similar_cases: List[Dict]) -> Dict[str, Any]:
        """
        Complete decision analysis using historian agent
        
        Args:
            decision_context: Information about the current decision
            similar_cases: Similar past cases from RAG retrieval
        
        Returns:
            Historical analysis results
        """
        # Historical Analysis
        print("Running Historian Agent...")
        historian_result = self.historian.analyze({
            'decision_context': self._format_decision_context(decision_context),
            'similar_cases': similar_cases
        })
        
        # Compile results
        results = {
            'decision_context': decision_context,
            'historian_analysis': historian_result,
            'similar_cases_count': len(similar_cases),
            'avg_similarity': self._calculate_avg_similarity(similar_cases)
        }
        
        return results
    
    def generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary for display
        
        Args:
            analysis_results: Results from analyze_decision
        
        Returns:
            Summary with key insights
        """
        historian = analysis_results['historian_analysis']
        
        summary = {
            'similar_cases_found': analysis_results['similar_cases_count'],
            'avg_similarity': analysis_results['avg_similarity'],
            'historical_pattern': self._extract_key_insight(historian),
            'analysis_output': historian.get('raw_output', 'No analysis available')
        }
        
        return summary
    
    def _format_decision_context(self, context: Dict) -> str:
        """Format decision context as string"""
        formatted = []
        for key, value in context.items():
            formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
    
    def _calculate_avg_similarity(self, cases: List[Dict]) -> float:
        """Calculate average similarity score"""
        if not cases:
            return 0.0
        scores = [case.get('score', 0) for case in cases]
        return sum(scores) / len(scores)
    
    def _extract_key_insight(self, agent_result: Dict) -> str:
        """Extract key insight from agent result"""
        output = agent_result.get('raw_output', '')
        if not output:
            return "No specific insights"
        
        sentences = output.split('.')
        return sentences[0][:200] + "..." if len(sentences[0]) > 200 else sentences[0]


# Example usage
if __name__ == "__main__":
    import os
    import sys
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    from rag_core.retriever.qdrant_retriever import QdrantRetriever
    
    # Set OpenAI API key
    # os.environ['OPENAI_API_KEY'] = 'your-key-here'
    
    # Initialize retriever and orchestrator
    retriever = QdrantRetriever()
    orchestrator = AgentOrchestrator(model_name="gpt-3.5-turbo")
    
    # Get a real client from Qdrant
    query = "client with high income, stable employment, owns property"
    print(f"Searching Qdrant for: {query}")
    results = retriever.search(query, top_k=1)
    
    if not results:
        print("No results found. Please ensure data is ingested to Qdrant.")
        sys.exit(1)
    
    # Use real client data
    client = results[0]
    print(f"\nAnalyzing Client {client['client_id']}...")
    print(f"Risk category: {'Default Risk' if client['target'] == 1 else 'Good Standing'}")
    
    # Build decision context from real data
    decision_context = {
        'client_id': client['client_id'],
        'target': client['target'],
        'profile_summary': client['text'][:300]
    }
    
    # Get similar cases from Qdrant
    similar_cases = retriever.search(client['text'][:200], top_k=10)
    print(f"Found {len(similar_cases)} similar cases\n")
    
    # Run analysis with real data
    print("Running historical decision analysis...\n")
    results = orchestrator.analyze_decision(
        decision_context=decision_context,
        similar_cases=similar_cases
    )
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    
    # Generate summary
    summary = orchestrator.generate_summary(results)
    print(f"\nSimilar Cases Found: {summary['similar_cases_found']}")
    print(f"Average Similarity: {summary['avg_similarity']:.3f}")
    print(f"\nKey Insight: {summary['historical_pattern']}")
    print(f"\nFull Analysis:\n{summary['analysis_output']}")
