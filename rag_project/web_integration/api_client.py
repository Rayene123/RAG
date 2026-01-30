"""
API Client for Decision Shadows
Handles communication with the backend API
"""
import requests
from typing import Dict, List, Optional, Any
import streamlit as st


class APIClient:
    """Client for interacting with the Decision Shadows API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "dev-test-key-12345"
        self.headers = {"X-API-Key": self.api_key}
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e}")
            return {}
        except Exception as e:
            st.error(f"Request failed: {e}")
            return {}
    
    # Health & Metrics
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            return self._handle_response(response)
        except:
            return {"status": "unavailable"}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            response = requests.get(f"{self.base_url}/metrics", headers=self.headers, timeout=5)
            return self._handle_response(response)
        except:
            return {}
    
    # Profile Endpoints
    def get_profile(self, client_id: int) -> Dict[str, Any]:
        """Get a single client profile"""
        response = requests.get(
            f"{self.base_url}/profile/{client_id}",
            headers=self.headers,
            timeout=10
        )
        return self._handle_response(response)
    
    def get_profiles_batch(self, client_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple client profiles"""
        response = requests.post(
            f"{self.base_url}/profile/batch",
            json={"client_ids": client_ids},
            headers=self.headers,
            timeout=10
        )
        result = self._handle_response(response)
        return result if isinstance(result, list) else []
    
    def list_profiles(self, offset: int = 0, limit: int = 10, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """List profiles with pagination"""
        params = {"offset": offset, "limit": limit}
        if filters:
            params["filters"] = filters
        
        response = requests.get(
            f"{self.base_url}/profiles",
            params=params,
            headers=self.headers,
            timeout=10
        )
        return self._handle_response(response)
    
    def get_analyzed_profile(self, client_id: int, alternatives: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Get profile with complete analysis"""
        params = {}
        if alternatives:
            params["alternatives"] = alternatives
        
        response = requests.get(
            f"{self.base_url}/profile/{client_id}/analyzed",
            params=params,
            headers=self.headers,
            timeout=30
        )
        return self._handle_response(response)
    
    # Search Endpoints
    def search_text(self, query: str, top_k: int = 5, use_llm: bool = True) -> Dict[str, Any]:
        """Perform text-based search"""
        response = requests.post(
            f"{self.base_url}/search/text",
            json={
                "query": query,
                "top_k": top_k,
                "use_llm_understanding": use_llm
            },
            headers=self.headers,
            timeout=30
        )
        return self._handle_response(response)
    
    
    def search_metadata(self, filters: Dict, top_k: int = 5) -> Dict[str, Any]:
        """Search using metadata filters only"""
        response = requests.post(
            f"{self.base_url}/search/metadata",
            json={
                "filters": filters,
                "top_k": top_k
            },
            headers=self.headers,
            timeout=30
        )
        return self._handle_response(response)
    
    def search_hybrid(self, query: str, filters: Dict, top_k: int = 5) -> Dict[str, Any]:
        """Hybrid search with text and filters"""
        response = requests.post(
            f"{self.base_url}/search/hybrid",
            json={
                "query": query,
                "filters": filters,
                "top_k": top_k
            },
            headers=self.headers,
            timeout=30
        )
        return self._handle_response(response)
    
    def search_pdf(self, pdf_file, top_k: int = 5) -> Dict[str, Any]:
        """Search using PDF document"""
        files = {"file": pdf_file}
        data = {"top_k": top_k}
        
        response = requests.post(
            f"{self.base_url}/search/pdf",
            files=files,
            data=data,
            headers=self.headers,
            timeout=60
        )
        return self._handle_response(response)
    
    def search_image(self, image_file, top_k: int = 5) -> Dict[str, Any]:
        """Search using image document"""
        files = {"file": image_file}
        data = {"top_k": top_k}
        
        response = requests.post(
            f"{self.base_url}/search/image",
            files=files,
            data=data,
            headers=self.headers,
            timeout=60
        )
        return self._handle_response(response)
    
    # Analysis Endpoints
    def analyze_historical(
        self, 
        decision_context: Dict,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Get historical analysis"""
        response = requests.post(
            f"{self.base_url}/analyze/historical",
            json={
                "decision_context": decision_context,
                "query": query,
                "top_k": top_k
            },
            headers=self.headers,
            timeout=30
        )
        return self._handle_response(response)
    
    def analyze_risk(
        self,
        decision_context: Dict,
        query: str,
        alternatives: Optional[List[Dict]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Get risk analysis"""
        payload = {
            "decision_context": decision_context,
            "query": query,
            "top_k": top_k
        }
        if alternatives:
            payload["alternatives"] = alternatives
        
        response = requests.post(
            f"{self.base_url}/analyze/risk",
            json=payload,
            headers=self.headers,
            timeout=30
        )
        return self._handle_response(response)
    
    def analyze_complete(
        self,
        decision_context: Dict,
        query: str,
        alternatives: Optional[List[Dict]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Get complete analysis (historical + risk)"""
        payload = {
            "decision_context": decision_context,
            "query": query,
            "top_k": top_k
        }
        if alternatives:
            payload["alternatives"] = alternatives
        
        response = requests.post(
            f"{self.base_url}/analyze/complete",
            json=payload,
            headers=self.headers,
            timeout=60
        )
        return self._handle_response(response)


@st.cache_resource
def get_api_client(base_url: str = "http://localhost:8000", api_key: Optional[str] = None) -> APIClient:
    """Get cached API client instance"""
    return APIClient(base_url=base_url, api_key=api_key)
