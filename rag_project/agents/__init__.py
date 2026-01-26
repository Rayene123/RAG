"""
Decision Shadows Agents Module

This module contains specialized AI agents for decision analysis:
- HistorianAgent: Analyzes past decision patterns
- RiskAgent: Assesses risk and calculates default probabilities
"""

from agents.base_agent import BaseAgent
from agents.historian_agent import HistorianAgent
from agents.risk_agent import RiskAgent

__all__ = [
    'BaseAgent',
    'HistorianAgent',
    'RiskAgent'
]
