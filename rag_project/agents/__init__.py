"""
Decision Shadows Agents Module

This module contains specialized AI agents for decision analysis:
- HistorianAgent: Analyzes past decision patterns
"""

from agents.base_agent import BaseAgent
from agents.historian_agent import HistorianAgent

__all__ = [
    'BaseAgent',
    'HistorianAgent'
]
