"""
bAIt Agents Module

This module provides AI agents for specialized analysis tasks. The agents are
organized into framework components, specialized agents, and persona configurations.

Agent Framework:
- BaseAgent: Abstract base class for all agents
- AgentOrchestrator: Multi-agent coordination
- QueryProcessor: Natural language query processing

Specialized Agents:
- DeploymentExpert: Deployment analysis specialist
- TroubleshootingAgent: Problem diagnosis specialist
- OptimizationAgent: Performance optimization specialist
- SecurityAgent: Security analysis specialist
- DocumentationAgent: Documentation analysis specialist
"""

from .framework import AgentOrchestrator, BaseAgent, QueryProcessor
from .specialized import (
    DeploymentExpert,
    DocumentationAgent,
    OptimizationAgent,
    SecurityAgent,
    TroubleshootingAgent,
)

__all__ = [
    "BaseAgent",
    "AgentOrchestrator",
    "QueryProcessor",
    "DeploymentExpert",
    "TroubleshootingAgent",
    "OptimizationAgent",
    "SecurityAgent",
    "DocumentationAgent"
]
