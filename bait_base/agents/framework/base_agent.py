"""
Base Agent Class for bAIt Framework

Abstract base class that defines the core interface for all bAIt agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentResult:
    """Result of agent execution"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    execution_time: Optional[float] = None


class BaseAgent(ABC):
    """
    Abstract base class for all bAIt agents.
    
    Provides common functionality for:
    - Status management
    - Logging
    - Result handling
    - Configuration management
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"bait.agents.{name}")
        self._results: List[AgentResult] = []
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Must be implemented by subclasses.
        
        Returns:
            AgentResult: Execution result with success status and data
        """
        pass
    
    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return self.status
    
    def get_results(self) -> List[AgentResult]:
        """Get all execution results"""
        return self._results.copy()
    
    def get_latest_result(self) -> Optional[AgentResult]:
        """Get most recent execution result"""
        return self._results[-1] if self._results else None
    
    def clear_results(self):
        """Clear all stored results"""
        self._results.clear()
        
    def _set_status(self, status: AgentStatus):
        """Internal method to update agent status"""
        self.status = status
        self.logger.debug(f"Agent {self.name} status changed to {status.value}")
        
    def _add_result(self, result: AgentResult):
        """Internal method to store execution result"""
        self._results.append(result)
        
    def _create_result(
        self, 
        success: bool, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        execution_time: Optional[float] = None
    ) -> AgentResult:
        """Helper method to create AgentResult"""
        return AgentResult(
            success=success,
            message=message,
            data=data,
            errors=errors,
            execution_time=execution_time
        )