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

The database has BOTH filterable metadata AND text descriptions:

FILTERABLE METADATA (use for exact matching):
- TARGET: 0 (paid back) or 1 (defaulted)
- CODE_GENDER: 'M', 'F'
- NAME_FAMILY_STATUS: 'Married', 'Single / not married', 'Civil marriage', 'Widow', 'Separated'
- NAME_EDUCATION_TYPE: 'Secondary / secondary special', 'Higher education', 'Incomplete higher', 'Lower secondary', 'Academic degree'
- NAME_INCOME_TYPE: 'Working', 'Commercial associate', 'Pensioner', 'State servant', 'Student'
- FLAG_OWN_CAR: 'Y', 'N'
- FLAG_OWN_REALTY: 'Y', 'N'
- NAME_HOUSING_TYPE: 'House / apartment', 'Rented apartment', 'With parents', 'Municipal apartment', 'Office apartment', 'Co-op apartment'
- OCCUPATION_TYPE: 'Laborers', 'Core staff', 'Sales staff', 'Managers', 'Drivers', 'High skill tech staff', 'Accountants', etc.
- NAME_CONTRACT_TYPE: 'Cash loans', 'Revolving loans'
- CNT_CHILDREN: integer (0, 1, 2, 3...)
- CNT_FAM_MEMBERS: integer
- DAYS_BIRTH: negative integer (age = -DAYS_BIRTH/365, young <35yrs = DAYS_BIRTH > -12775)
- DAYS_EMPLOYED: negative integer (stable >5yrs = DAYS_EMPLOYED < -1825)
- AMT_INCOME_TOTAL: float (low <150k, middle 150k-300k, high >300k)
- AMT_CREDIT: float
- OWN_CAR_AGE: float

TEXT (for semantic search):
- Credit history descriptions, payment patterns, risk reasoning

Return a JSON object with:
{
  "intent": "default" or "good_standing" or null,
  "filters": {
    "target": 1 or 0,
    "CODE_GENDER": "M" or "F",
    "NAME_FAMILY_STATUS": "Married",
    "FLAG_OWN_REALTY": "Y" or "N",
    "CNT_CHILDREN": integer,
    "DAYS_BIRTH_range": {"gte": -12775, "lte": 0},
    "DAYS_EMPLOYED_range": {"lte": -1825},
    "AMT_INCOME_TOTAL_range": {"gte": 300000} or {"lte": 150000}
  },
  "detected_attributes": ["Payment Status: DEFAULTED", "Gender: FEMALE", "Income: HIGH"],
  "search_query": "remaining terms for semantic search",
  "explanation": "Brief explanation"
}

Examples:

Query: "Find young married female clients who didn't pay"
Response: {
  "intent": "default",
  "filters": {
    "target": 1,
    "CODE_GENDER": "F",
    "NAME_FAMILY_STATUS": "Married",
    "DAYS_BIRTH_range": {"gte": -12775, "lte": 0}
  },
  "detected_attributes": ["Payment Status: DEFAULTED", "Gender: FEMALE", "Marital Status: MARRIED", "Age: YOUNG (<35)"],
  "search_query": "",
  "explanation": "Filtering by TARGET=1, female, married, age <35. All criteria covered by filters."
}

Query: "Show high income clients who own real estate and paid back"
Response: {
  "intent": "good_standing",
  "filters": {
    "target": 0,
    "FLAG_OWN_REALTY": "Y",
    "AMT_INCOME_TOTAL_range": {"gte": 300000}
  },
  "detected_attributes": ["Payment Status: PAID BACK", "Assets: OWNS REAL ESTATE", "Income: HIGH (>300k)"],
  "search_query": "",
  "explanation": "Filtering by TARGET=0, owns real estate, income >300k. Fully filterable."
}

Query: "Find clients with 2 children and stable employment"
Response: {
  "intent": null,
  "filters": {
    "CNT_CHILDREN": 2,
    "DAYS_EMPLOYED_range": {"lte": -1825}
  },
  "detected_attributes": ["Children: 2", "Employment: STABLE (>5 years)"],
  "search_query": "",
  "explanation": "Filtering by 2 children and 5+ years employment."
}

Query: "Show pensioners with low payment completion who defaulted"
Response: {
  "intent": "default",
  "filters": {
    "target": 1,
    "NAME_INCOME_TYPE": "Pensioner"
  },
  "detected_attributes": ["Payment Status: DEFAULTED", "Income Type: PENSIONER", "Payment Behavior: LOW COMPLETION"],
  "search_query": "low payment completion ratio percentage",
  "explanation": "Filtering by TARGET=1 and pensioner status. Semantic search for low payment completion."
}

IMPORTANT:
- Use filters for ANY attribute that matches available metadata fields
- Use search_query ONLY for vague concepts or payment patterns not in metadata
- For age ranges: young <35 = DAYS_BIRTH > -12775, old >55 = DAYS_BIRTH < -20075
- DAYS are NEGATIVE: more negative = older/longer
- Always return valid JSON, no markdown."""
    
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
                'filters': parsed_llm.get('filters', {}),
                'intent': parsed_llm.get('intent'),
                'detected_filters': parsed_llm.get('detected_attributes', []),
                'explanation': parsed_llm.get('explanation', '')
            }
            
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
