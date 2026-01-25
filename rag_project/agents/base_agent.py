"""
Base Agent class for Decision Shadows
All specialized agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain


class BaseAgent(ABC):
    """Base class for all Decision Shadow agents"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize base agent with LLM
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature (0-1)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        self.chain = None
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the given context and return results
        
        Args:
            context: Dictionary containing relevant context for analysis
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def _create_chain(self, prompt_template: str) -> LLMChain:
        """
        Create LangChain chain with given prompt
        
        Args:
            prompt_template: The prompt template string
            
        Returns:
            Configured LLMChain
        """
        prompt = PromptTemplate.from_template(prompt_template)
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def _format_similar_cases(self, cases: List[Dict]) -> str:
        """
        Format similar cases for LLM consumption
        
        Args:
            cases: List of similar cases from RAG retrieval
            
        Returns:
            Formatted string representation
        """
        if not cases:
            return "No similar cases found."
        
        formatted = []
        for i, case in enumerate(cases, 1):
            formatted.append(
                f"Case {i} (Similarity: {case.get('score', 0):.3f}):\n"
                f"Client ID: {case.get('client_id', 'N/A')}\n"
                f"Target: {case.get('target', 'N/A')}\n"
                f"Details: {case.get('text', '')[:200]}...\n"
            )
        return "\n".join(formatted)
