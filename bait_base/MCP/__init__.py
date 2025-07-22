"""
bAIt MCP (Model Context Protocol) Integration

This module provides MCP servers, tools, and resources for Claude Code integration.
The MCP integration allows Claude Code to interact with bAIt analysis capabilities
through standardized protocols.

MCP Servers:
- bAIt Analysis Server: Main analysis capabilities
- Deployment Query Server: Deployment-specific querying
- Troubleshooting Server: Problem diagnosis
- Visualization Server: Diagram generation

MCP Tools:
- Deployment analysis tools
- Query processing tools
- Visualization generation tools
- Report generation tools

MCP Resources:
- Deployment data access
- Analysis results
- Knowledge base access
"""

from .resources import *
from .servers import *
from .tools import *

__all__ = ["servers", "tools", "resources"]
