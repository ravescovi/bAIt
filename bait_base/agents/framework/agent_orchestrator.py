"""
Agent Orchestrator for bAIt Framework

Coordinates multiple agents for complex analysis tasks.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from .base_agent import BaseAgent, AgentResult


class AgentOrchestrator:
    """
    Orchestrates multiple agents for complex tasks.
    
    Features:
    - Multi-agent coordination
    - Task distribution
    - Result aggregation
    - Error handling and recovery
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("bait.agents.orchestrator")
        self.registered_agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, name: str, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.registered_agents[name] = agent
        self.logger.debug(f"Registered agent: {name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name"""
        return self.registered_agents.get(name)
    
    async def execute_multi_agent_task(
        self, 
        task_plan: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """Execute a multi-agent task based on task plan"""
        results = {}
        
        for agent_name, task_config in task_plan.items():
            if agent_name in self.registered_agents:
                agent = self.registered_agents[agent_name]
                result = await agent.execute(**task_config)
                results[agent_name] = result
            else:
                self.logger.error(f"Agent not registered: {agent_name}")
                
        return results