# Claude Code Integration Guide

This guide provides comprehensive instructions for integrating bAIt with Claude Code using the Model Context Protocol (MCP).

## Overview

bAIt provides native MCP servers that expose its analysis capabilities to Claude Code, enabling natural language interactions with beamline deployment configurations. This integration allows Claude Code to:

- Analyze deployment configurations
- Answer questions about system architecture
- Provide troubleshooting assistance
- Generate visualizations and reports
- Offer optimization recommendations

## Prerequisites

### System Requirements
- **bAIt installed**: Version 0.1.0 or higher
- **Claude Code**: Latest version with MCP support
- **Python**: 3.11 or higher
- **Network access**: Between Claude Code and bAIt MCP servers

### Knowledge Requirements
- Basic understanding of beamline operations
- Familiarity with Claude Code interface
- Understanding of MCP concepts (optional but helpful)

## Installation and Setup

### Step 1: Install bAIt with MCP Support

```bash
# Install bAIt with MCP dependencies
pip install "bait[mcp]"

# Or for development
cd bait_base/
pip install -e ".[dev,mcp]"
```

### Step 2: Configure Deployment

Ensure you have a properly configured bAIt deployment:

```bash
# Create or verify deployment configuration
bait-create-deployment 8id-bits
bait-analyze 8id-bits

# Verify deployment is working
bait-query 8id-bits "What IOCs are configured?"
```

### Step 3: Start MCP Server

```bash
# Start MCP server for specific deployment
bait-mcp-server --deployment 8id-bits

# Or start with auto-discovery of all deployments
bait-mcp-server --auto-discover

# Start with custom configuration
bait-mcp-server --config custom-mcp-config.json
```

Server will start on default port 8000 and provide:
- **Analysis tools**: Deployment analysis capabilities
- **Query tools**: Natural language querying
- **Visualization tools**: Diagram generation
- **Resource access**: Deployment data and analysis results

### Step 4: Configure Claude Code

Add bAIt MCP server to Claude Code configuration:

#### Option A: Automatic Configuration
```json
{
  "mcp_servers": {
    "bait": {
      "command": "bait-mcp-server",
      "args": ["--deployment", "8id-bits"]
    }
  }
}
```

#### Option B: Manual Configuration
```json
{
  "mcp_servers": {
    "bait": {
      "command": "python",
      "args": ["-m", "bait.MCP.servers.main", "--deployment", "8id-bits"],
      "env": {
        "BAIT_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Option C: Multi-Deployment Configuration
```json
{
  "mcp_servers": {
    "bait-8id": {
      "command": "bait-mcp-server",
      "args": ["--deployment", "8id-bits"]
    },
    "bait-12id": {
      "command": "bait-mcp-server", 
      "args": ["--deployment", "12id-bits"]
    }
  }
}
```

## Available MCP Tools

### Analysis Tools

#### `analyze_deployment`
Perform comprehensive deployment analysis.

**Usage in Claude Code:**
```
Human: @bait analyze the 8-ID beamline deployment

Claude: I'll analyze the 8-ID beamline deployment using bAIt...
[Calls analyze_deployment tool]

Analysis Results:
✅ 12 IOCs configured and operational
✅ 45 Bluesky devices properly mapped
✅ 23 MEDM screens validated
⚠️  2 configuration inconsistencies found
🔧 3 optimization recommendations available

Would you like me to detail any specific findings?
```

#### `query_deployment`
Natural language querying of deployment configuration.

**Usage in Claude Code:**
```
Human: @bait what detectors are configured for the 8-ID beamline?

Claude: Let me query the 8-ID detector configuration...
[Calls query_deployment tool]

Detector Configuration:
🔍 Lambda Detector (DET1):
   • IOC: detector_ioc_1
   • Resolution: 2048x2048 pixels
   • Exposure range: 0.1-10 seconds
   • Status: Operational

🔍 Pilatus Detector (DET2):
   • IOC: detector_ioc_2
   • Resolution: 1024x1024 pixels
   • Exposure range: 0.01-1 second
   • Status: Operational
```

### Troubleshooting Tools

#### `troubleshoot_issue`
AI-powered troubleshooting assistance.

**Usage in Claude Code:**
```
Human: @bait the detector scan is failing, help me troubleshoot

Claude: I'll analyze the detector scan issue...
[Calls troubleshoot_issue tool]

Troubleshooting Analysis:
🔍 Issue: Detector scan failures
🎯 Most likely cause: Detector readout timeout
📊 Evidence: 3 recent timeouts, detector response slow

Recommended Actions:
1. Check detector IOC status
2. Verify network connectivity
3. Increase timeout settings
4. Test detector hardware

Would you like me to provide detailed steps for any of these actions?
```

### Visualization Tools

#### `generate_visualization`
Create system diagrams and visualizations.

**Usage in Claude Code:**
```
Human: @bait create a network diagram for the 8-ID beamline

Claude: I'll generate a network topology diagram for 8-ID...
[Calls generate_visualization tool]

Network Diagram Generated:
📊 Diagram type: Network topology
🖼️  Format: Interactive SVG
📁 Location: /tmp/8id-network-diagram.svg
🔗 Components shown: 15 hosts, 12 IOCs, 3 switches

The diagram shows:
• All network connections
• IOC host assignments
• Service port mappings
• Network traffic flows

[Displays interactive diagram]
```

#### `generate_report`
Create comprehensive analysis reports.

**Usage in Claude Code:**
```
Human: @bait generate a system health report for 8-ID

Claude: I'll create a comprehensive system health report...
[Calls generate_report tool]

System Health Report Generated:
📋 Report type: System health assessment
📊 Overall health score: 94/100 (Excellent)
⚠️  Issues identified: 2 minor warnings
🔧 Recommendations: 5 optimization suggestions

Key findings:
• All critical systems operational
• Performance within normal ranges
• Minor configuration optimization needed
• Preventive maintenance recommended

[Provides detailed report with charts and metrics]
```

### Resource Access Tools

#### `get_deployment_data`
Access deployment configuration and analysis data.

**Usage in Claude Code:**
```
Human: @bait show me the IOC configuration for the motor controller

Claude: Let me retrieve the motor controller IOC configuration...
[Calls get_deployment_data tool]

Motor Controller IOC Configuration:
🔧 IOC Name: motor_ioc
📂 Location: /home/8id/iocs/motor_ioc/
🚀 Startup: st.cmd
💾 Database: motors.db

Configuration Details:
• 8 motors configured
• ESP301 controller
• Network port: 5064
• Update rate: 10 Hz
• Position accuracy: ±0.1 μm

[Shows detailed configuration parameters]
```

## Advanced Usage Patterns

### Multi-Step Analysis Workflows

```
Human: @bait I need to understand why my temperature scans are failing

Claude: I'll help you analyze the temperature scan failures systematically.

First, let me check the current system status...
[Calls analyze_deployment with focus on temperature system]

Now let me examine recent scan failures...
[Calls query_deployment for scan failure patterns]

Let me troubleshoot the specific issue...
[Calls troubleshoot_issue for temperature scan problems]

Based on my analysis:

🔍 Root Cause: Temperature controller PID tuning suboptimal
📊 Evidence: 
   • 23% scan failure rate
   • Temperature overshoot >2°C
   • Stabilization time >60 seconds

🔧 Recommended Solution:
1. Retune PID parameters
2. Increase scan wait times
3. Implement temperature stability checks

Would you like me to provide detailed PID tuning procedures?
```

### Comparative Analysis

```
Human: @bait compare the detector configurations between 8-ID and 12-ID

Claude: I'll compare detector configurations across both beamlines...
[Calls query_deployment for both deployments]

Detector Configuration Comparison:
══════════════════════════════════

8-ID Beamline:
🔍 Detectors: 2 (Lambda, Pilatus)
📊 Total pixels: 6.3M
⚡ Max frame rate: 1000 Hz
🔧 Readout time: 3.2ms

12-ID Beamline:
🔍 Detectors: 3 (CCD, Pilatus, Lambda)
📊 Total pixels: 8.1M
⚡ Max frame rate: 500 Hz
🔧 Readout time: 5.8ms

Key Differences:
• 12-ID has additional CCD detector
• 8-ID optimized for high-speed acquisition
• 12-ID better for high-resolution imaging
• Both use similar Pilatus/Lambda combination

Recommendations:
• 8-ID: Consider adding CCD for versatility
• 12-ID: Optimize readout for speed if needed
```

### Automated Reporting

```
Human: @bait create a weekly status report for all our beamlines

Claude: I'll generate comprehensive weekly reports for all configured beamlines...
[Calls generate_report for multiple deployments]

Weekly Status Report Summary:
═══════════════════════════

📊 Overall Status: 3/4 beamlines operational
✅ 8-ID: Excellent (98/100)
✅ 12-ID: Good (87/100)
✅ USAXS: Excellent (96/100)
⚠️  16-BM: Issues detected (74/100)

Key Highlights:
• Total experiments: 47 (95% success rate)
• Uptime average: 97.3%
• Performance trends: Stable
• Issues resolved: 12
• Pending maintenance: 3 items

Detailed reports generated for:
• System health metrics
• Performance trends
• Issue summaries
• Maintenance recommendations

[Provides links to detailed reports]
```

## Integration Best Practices

### Effective Prompt Patterns

#### 1. Specific Component Focus
```
Good: "@bait analyze the detector system performance"
Better: "@bait analyze the Lambda detector on IOC detector_ioc_1"
```

#### 2. Context-Rich Queries
```
Good: "@bait why is my scan failing?"
Better: "@bait why is my temperature-dependent grid scan failing after 3 points?"
```

#### 3. Multi-Step Investigations
```
Good: "@bait troubleshoot the motor issue"
Better: "@bait first check motor IOC status, then analyze movement performance, then suggest solutions"
```

### Error Handling

#### Connection Issues
```
Human: @bait analyze the system

Claude: I'm having trouble connecting to the bAIt MCP server. Let me check...

Error: Connection refused on port 8000

Troubleshooting steps:
1. Verify MCP server is running: `ps aux | grep bait-mcp`
2. Check port availability: `netstat -ln | grep 8000`
3. Restart server: `bait-mcp-server --deployment 8id-bits`
4. Check firewall settings

Would you like me to help diagnose this connection issue?
```

#### Deployment Configuration Issues
```
Human: @bait query the 8-ID deployment

Claude: I encountered an issue accessing the 8-ID deployment configuration.

Error: Deployment '8id-bits' not found or not properly configured

Possible solutions:
1. Check deployment exists: `ls bait_deployments/8id-bits/`
2. Verify configuration: `bait-validate 8id-bits`
3. Run initial analysis: `bait-analyze 8id-bits`
4. Check MCP server deployment setting

Let me help you resolve this configuration issue.
```

### Performance Optimization

#### Server Configuration
```json
{
  "mcp_servers": {
    "bait": {
      "command": "bait-mcp-server",
      "args": [
        "--deployment", "8id-bits",
        "--cache-enabled",
        "--max-workers", "4",
        "--timeout", "30"
      ]
    }
  }
}
```

#### Resource Management
```bash
# Configure resource limits
export BAIT_MAX_MEMORY=2G
export BAIT_CACHE_SIZE=1G
export BAIT_WORKER_THREADS=4

# Start with resource monitoring
bait-mcp-server --deployment 8id-bits --monitor-resources
```

## Security Considerations

### Access Control
```json
{
  "mcp_servers": {
    "bait": {
      "command": "bait-mcp-server",
      "args": [
        "--deployment", "8id-bits",
        "--auth-required",
        "--allowed-users", "beamline_staff",
        "--log-access"
      ]
    }
  }
}
```

### Network Security
```bash
# Restrict server binding
bait-mcp-server --bind 127.0.0.1 --port 8000

# Enable SSL/TLS
bait-mcp-server --ssl-cert cert.pem --ssl-key key.pem
```

### Audit Logging
```bash
# Enable comprehensive logging
export BAIT_LOG_LEVEL=INFO
export BAIT_LOG_FILE=/var/log/bait-mcp.log
export BAIT_AUDIT_ENABLED=true
```

## Troubleshooting Integration Issues

### Common Problems and Solutions

#### 1. MCP Server Not Starting
```bash
# Check Python environment
python -c "import bait; print(bait.__version__)"

# Verify MCP dependencies
pip install "bait[mcp]"

# Check port availability
lsof -i :8000

# Start with debug logging
bait-mcp-server --deployment 8id-bits --debug
```

#### 2. Claude Code Not Finding Server
```bash
# Verify Claude Code MCP configuration
cat ~/.config/claude-code/mcp_settings.json

# Test MCP connection
curl -X POST http://localhost:8000/mcp/list_tools

# Check server logs
tail -f ~/.bait/logs/mcp.log
```

#### 3. Performance Issues
```bash
# Monitor resource usage
top -p $(pgrep bait-mcp)

# Check cache performance
bait-mcp-server --deployment 8id-bits --cache-stats

# Optimize worker threads
bait-mcp-server --deployment 8id-bits --workers 8
```

## Support and Resources

### Documentation
- **MCP Protocol**: https://modelcontextprotocol.io/
- **bAIt MCP API**: `/bait_base/docs/api/mcp.md`
- **Claude Code MCP**: https://docs.anthropic.com/claude/docs/mcp

### Community Resources
- **GitHub Issues**: https://github.com/ravescovi/bAIt/issues
- **Discussions**: https://github.com/ravescovi/bAIt/discussions
- **Examples**: `/bait_base/docs/examples/mcp-integration/`

### Professional Support
- **Training**: Available for beamline teams
- **Custom Integration**: Tailored MCP server development
- **Consulting**: Optimization and troubleshooting services

This integration guide ensures successful deployment of bAIt with Claude Code, providing powerful AI-assisted analysis capabilities for beamline operations.