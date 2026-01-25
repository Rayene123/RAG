"""
Base Agent class for Decision Shadows
All specialized agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI

# Load environment variables from .env file
load_dotenv()


class BaseAgent(ABC):
    """Base class for all Decision Shadow agents"""
    
    def __init__(self, model_name: str = "mistral-small-latest", temperature: float = 0.7):
        """
        Initialize base agent with Mistral AI (FREE tier available)
        
        Get your free API key at: https://console.mistral.ai/
        Set it as: MISTRAL_API_KEY environment variable
        
        Args:
            model_name: Mistral model (mistral-small-latest, mistral-large-latest, open-mistral-7b)
            temperature: Model temperature (0-1)
        """
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        
        if not mistral_api_key:
            raise ValueError(
                "MISTRAL_API_KEY not found! Get your free key at https://console.mistral.ai/\n"
                "Then set it: $env:MISTRAL_API_KEY='your-key-here' (PowerShell)"
            )
        
        self.llm = ChatMistralAI(
            model=model_name,
            temperature=temperature,
            mistral_api_key=mistral_api_key
        )
    
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
    
    def _create_chain(self, prompt_template: str):
        """
        Create LangChain chain with given prompt (using modern LCEL)
        
        Args:
            prompt_template: The prompt template string
            
        Returns:
            Configured chain (prompt | llm)
        """
        prompt = PromptTemplate.from_template(prompt_template)
        return prompt | self.llm
    
    def _format_similar_cases(self, cases: List[Dict]) -> str:
        """
        Format similar cases for LLM consumption with detailed metadata
        
        Args:
            cases: List of similar cases from RAG retrieval
            
        Returns:
            Formatted string representation with full details
        """
        if not cases:
            return "No similar cases found."
        
        formatted = []
        for i, case in enumerate(cases, 1):
            # Extract metadata
            metadata = case.get('metadata', {})
            payload = case.get('payload', {})
            
            # Build detailed case info
            case_info = [
                f"═══ Case {i} (Similarity Score: {case.get('score', 0):.4f}) ═══",
                f"Client ID: {case.get('client_id') or metadata.get('client_id') or payload.get('client_id', 'N/A')}",
                f"Target/Outcome: {case.get('target') or metadata.get('target') or payload.get('target', 'N/A')}",
            ]
            
            # Add all available metadata fields
            if metadata:
                case_info.append("\nClient Profile:")
                for key, value in metadata.items():
                    if key not in ['client_id', 'target', 'text']:
                        case_info.append(f"  • {key}: {value}")
            
            # Add text content
            text = case.get('text') or metadata.get('text') or payload.get('text', '')
            if text:
                case_info.append(f"\nFull Context:\n{text}")
            
            formatted.append("\n".join(case_info))
        
        return "\n\n".join(formatted)
