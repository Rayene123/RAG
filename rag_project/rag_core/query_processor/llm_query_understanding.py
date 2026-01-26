"""
LLM-based Query Understanding Layer
Uses LLM to parse natural language queries and extract intent/filters
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMQueryUnderstanding:
    """
    Uses an LLM to parse natural language queries and extract:
    - Payment status intent (target filter)
    - Income filters
    - Age filters
    - Other demographic/financial filters
    """
    
    def __init__(self, llm_provider: str = "mistral"):
        """
        Initialize LLM query understanding
        
        Args:
            llm_provider: 'mistral' or 'openai' (default: mistral)
        """
        self.llm_provider = llm_provider
        self._llm = None
        
        # System prompt for query understanding
        self.system_prompt = """You are a query understanding assistant for a credit risk RAG system.

The database stores client profiles as TEXT descriptions. Each profile includes:
- Demographics: age, gender, marital status, children, education
- Employment: occupation, years employed, income
- Assets: car ownership, real estate ownership, housing type
- Credit history: payment behavior, overdue amounts, credit amounts, approval rates
- Risk status: whether they defaulted or paid back

IMPORTANT: Only the TARGET field exists as filterable metadata:
- TARGET = 0: Client PAID BACK the loan (good standing, successful repayment, low risk)
- TARGET = 1: Client DEFAULTED (didn't pay, failed to repay, high risk)

ALL OTHER attributes (age, gender, income, marital status, etc.) are in TEXT format and must be searched semantically.

Your task:
1. Extract payment status intent → set target filter (0 or 1)
2. For all other criteria → create an optimized semantic search query that will match the text descriptions

Return a JSON object with:
{
  "intent": "default" or "good_standing" or null,
  "target_filter": 1 (defaulted) or 0 (paid back) or null,
  "detected_attributes": ["Age: YOUNG", "Marital Status: MARRIED", "Income: LOW"],
  "search_query": "optimized query matching text descriptions",
  "explanation": "Brief explanation"
}

Examples:

Query: "Find clients with low income and didn't pay the loan"
Response: {
  "intent": "default",
  "target_filter": 1,
  "detected_attributes": ["Payment Status: DEFAULTED", "Income: LOW"],
  "search_query": "low income annual income clients",
  "explanation": "Filtering by TARGET=1 (defaulted), searching semantically for low income profiles."
}

Query: "Show me young married female clients who successfully repaid"
Response: {
  "intent": "good_standing",
  "target_filter": 0,
  "detected_attributes": ["Payment Status: PAID BACK", "Age: YOUNG", "Gender: FEMALE", "Marital Status: MARRIED"],
  "search_query": "young female married client age years",
  "explanation": "Filtering by TARGET=0 (paid back), searching semantically for young married female clients."
}

Query: "Find high income clients who own real estate and defaulted"
Response: {
  "intent": "default",
  "target_filter": 1,
  "detected_attributes": ["Payment Status: DEFAULTED", "Income: HIGH", "Assets: OWNS REAL ESTATE"],
  "search_query": "high income annual income owns real estate yes asset ownership",
  "explanation": "Filtering by TARGET=1, searching semantically for high income clients with real estate."
}

Query: "Show elderly pensioners with stable employment who paid back"
Response: {
  "intent": "good_standing",
  "target_filter": 0,
  "detected_attributes": ["Payment Status: PAID BACK", "Age: ELDERLY", "Income Type: PENSIONER", "Employment: STABLE"],
  "search_query": "elderly old age pensioner stable employment years employed",
  "explanation": "Filtering by TARGET=0, searching semantically for elderly pensioners with stable employment."
}

Query: "Find clients with children and low payment completion"
Response: {
  "intent": null,
  "target_filter": null,
  "detected_attributes": ["Has Children: YES", "Payment Behavior: LOW COMPLETION"],
  "search_query": "children cnt payment completion ratio low percentage",
  "explanation": "No payment status filter. Searching semantically for clients with children and low payment completion."
}

IMPORTANT TIPS for search_query:
- Use keywords that appear in text descriptions: "annual income", "years old", "owns real estate", "married", "payment completion ratio"
- Include variations: "young" = "age 25", "high income" = "annual income 300000"
- For numeric ranges, use descriptive terms: "low income" not "$50k"
- Keep payment status keywords ONLY if no target_filter set

Always return valid JSON only, no markdown."""
    
    @property
    def llm(self):
        """Lazy load LLM"""
        if self._llm is None:
            self._initialize_llm()
        return self._llm
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider"""
        if self.llm_provider == "mistral":
            try:
                from langchain_mistralai import ChatMistralAI
                
                api_key = os.getenv("MISTRAL_API_KEY")
                if not api_key:
                    raise ValueError(
                        "MISTRAL_API_KEY not found in environment. "
                        "Set it with: $env:MISTRAL_API_KEY='your-key'"
                    )
                
                self._llm = ChatMistralAI(
                    model="mistral-small-latest",  # Fast and cost-effective
                    temperature=0.1,  # Low temperature for consistent parsing
                    mistral_api_key=api_key
                )
                print("✅ LLM Query Understanding initialized (Mistral)")
                
            except ImportError:
                raise ImportError(
                    "langchain-mistralai not installed. "
                    "Install with: pip install langchain-mistralai"
                )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query using LLM
        
        Args:
            query: Natural language query string
            
        Returns:
            Dict with:
                - original_query: str
                - search_query: str (cleaned for semantic search)
                - filters: dict of filters to apply
                - intent: str (payment status intent)
                - detected_filters: list of detected filter descriptions
                - explanation: str (LLM's explanation)
        """
        try:
            # Call LLM with the query
            response = self.llm.invoke([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Parse this query:\n\n{query}"}
            ])
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                content = response.content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                elif content.startswith("```"):
                    content = content.replace("```", "").strip()
                
                parsed_llm = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"⚠️  LLM returned invalid JSON: {e}")
                print(f"   Response: {response.content[:200]}...")
                # Fallback to basic parsing
                return self._create_fallback_result(query)
            
            # Build result structure
            result = {
                'original_query': query,
                'search_query': parsed_llm.get('search_query', query),
                'filters': {},
                'intent': parsed_llm.get('intent'),
                'detected_filters': parsed_llm.get('detected_attributes', []),
                'explanation': parsed_llm.get('explanation', '')
            }
            
            # Add target filter if detected
            if parsed_llm.get('target_filter') is not None:
                result['filters']['target'] = parsed_llm['target_filter']
            
            return result
        
        except Exception as e:
            print(f"⚠️  Error in LLM query parsing: {e}")
            return self._create_fallback_result(query)
    
    def _create_fallback_result(self, query: str) -> Dict[str, Any]:
        """Create fallback result when LLM fails"""
        return {
            'original_query': query,
            'search_query': query,
            'filters': {},
            'intent': None,
            'detected_filters': [],
            'explanation': 'LLM parsing failed, using direct search'
        }
    
    def explain_understanding(self, parsed: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of what was understood
        
        Args:
            parsed: Result from parse_query()
            
        Returns:
            Explanation string
        """
        lines = ["🧠 Query Understanding:"]
        
        if parsed.get('explanation'):
            lines.append(f"   {parsed['explanation']}")
        
        if parsed['detected_filters']:
            lines.append("   Detected Filters:")
            for f in parsed['detected_filters']:
                lines.append(f"   - {f}")
        else:
            lines.append("   No specific filters detected")
        
        if parsed['search_query'] != parsed['original_query']:
            lines.append(f"   Semantic Search: '{parsed['search_query']}'")
        
        return "\n".join(lines)


# Convenience function
def parse_natural_query(query: str, llm_provider: str = "mistral") -> Dict[str, Any]:
    """
    Parse a natural language query using LLM
    
    Args:
        query: Natural language query
        llm_provider: 'mistral' or 'openai'
        
    Returns:
        Parsed query dict with filters and cleaned search query
    """
    understanding = LLMQueryUnderstanding(llm_provider=llm_provider)
    return understanding.parse_query(query)
