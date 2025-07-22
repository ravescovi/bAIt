# bAIt Beamline Deployment Guide

This guide provides step-by-step instructions for deploying bAIt at a beamline facility.

## Overview

bAIt is an **analysis-only** system that provides intelligent insights into beamline configurations without interfering with operations. It analyzes existing deployments and answers questions about system architecture, troubleshooting, and optimization.

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Operating System**: Linux (preferred), macOS, or Windows
- **Memory**: 8GB minimum, 16GB recommended
- **Storage**: 10GB for installation, additional space for analysis cache
- **Network**: Access to beamline repositories (GitHub, GitLab, etc.)

### Access Requirements
- **Repository Access**: SSH keys or access tokens for IOC, BITS, and MEDM repositories
- **Network Access**: Ability to reach beamline hosts (optional, for real-time monitoring)
- **File System Access**: Read access to local copies of configurations

## Phase 1: Initial Setup

### Step 1: Install bAIt

#### Option A: Production Installation
```bash
pip install bait
```

#### Option B: Development Installation
```bash
git clone https://github.com/ravescovi/bAIt.git
cd bAIt/bait_base/
pip install -e ".[dev]"
```

### Step 2: Verify Installation
```bash
# Check installation
bait-analyze --version

# Test basic functionality
bait-create-deployment test
bait-analyze test --dry-run
```

### Step 3: Create Deployment Configuration

#### Create New Deployment
```bash
# Replace "8id-bits" with your beamline identifier
bait-create-deployment 8id-bits
```

This creates:
```
bait_deployments/8id-bits/
├── config.json         # Main configuration
├── analysis_cache/     # Cached results
├── reports/           # Generated reports
└── custom_configs/    # Custom settings
```

#### Edit Configuration
```bash
cd bait_deployments/8id-bits/
vim config.json
```

Update the following sections:

**Deployment Metadata:**
```json
{
  "deployment": {
    "name": "8id-bits",
    "description": "8-ID Dynamic Scattering Beamline",
    "beamline": "8-ID",
    "sector": "8",
    "maintainer": "8-ID Team",
    "contact": "8id-team@aps.anl.gov"
  }
}
```

**Source Repositories:**
```json
{
  "sources": {
    "iocs": {
      "repository": "https://github.com/aps-8id/8id-iocs",
      "branch": "main",
      "local_path": "/home/8id/iocs",
      "folders": [
        {
          "name": "motor_ioc",
          "description": "Motor control IOC",
          "startup_file": "st.cmd",
          "database_files": ["motors.db"]
        }
      ]
    },
    "bits_deployment": {
      "repository": "https://github.com/aps-8id/8id-bits",
      "branch": "production",
      "local_path": "/home/8id/bluesky",
      "startup_file": "src/id8_i/startup.py"
    },
    "medm_screens": {
      "repository": "https://github.com/aps-8id/8id-medm",
      "branch": "main",
      "local_path": "/home/8id/medm"
    }
  }
}
```

**Network Configuration:**
```json
{
  "network": {
    "subnet": "164.54.xxx.xxx/24",
    "hosts": [
      {
        "name": "8id-ws1",
        "ip": "164.54.xxx.100",
        "role": "workstation"
      },
      {
        "name": "8id-ioc1",
        "ip": "164.54.xxx.101",
        "role": "ioc_host"
      }
    ]
  }
}
```

### Step 4: Initial Analysis

#### Run First Analysis
```bash
bait-analyze 8id-bits
```

This will:
- Clone/update repositories
- Analyze IOC configurations
- Process Bluesky device mappings
- Parse MEDM screens
- Build knowledge base
- Generate initial reports

#### Verify Analysis Results
```bash
# Check analysis status
bait-report 8id-bits --format status

# View component inventory
bait-query 8id-bits "What components are configured?"

# Generate system overview
bait-visualize 8id-bits --type overview
```

## Phase 2: Integration with Workflows

### Daily Operations Integration

#### Morning System Check
Create a daily startup script:
```bash
#!/bin/bash
# daily-check.sh

echo "=== Daily bAIt System Check ==="
echo "Date: $(date)"
echo

# Quick system status
echo "System Status:"
bait-query 8id-bits "What's the current system status?" --brief

# Check for configuration changes
echo -e "\nConfiguration Changes:"
bait-analyze 8id-bits --check-changes --since yesterday

# Generate daily report
echo -e "\nGenerating daily report..."
bait-report 8id-bits --format daily --output reports/daily-$(date +%Y%m%d).html

echo "Daily check complete!"
```

#### Troubleshooting Workflow
Create troubleshooting helpers:
```bash
#!/bin/bash
# troubleshoot.sh

ISSUE="$1"
COMPONENT="$2"

echo "=== bAIt Troubleshooting Assistant ==="
echo "Issue: $ISSUE"
echo "Component: $COMPONENT"
echo

# Get AI-powered troubleshooting advice
bait-query 8id-bits "Help me troubleshoot: $ISSUE with $COMPONENT"

# Show relevant dependencies
bait-visualize 8id-bits --type dependencies --highlight "$COMPONENT"

# Generate troubleshooting report
bait-report 8id-bits --troubleshooting --component "$COMPONENT" --issue "$ISSUE"
```

### Development Integration

#### Pre-Deployment Validation
```bash
#!/bin/bash
# validate-changes.sh

COMPONENT="$1"
CHANGE_DESC="$2"

echo "=== Pre-Deployment Validation ==="
echo "Component: $COMPONENT"
echo "Change: $CHANGE_DESC"
echo

# Analyze potential impact
bait-analyze 8id-bits --impact-analysis "$COMPONENT"

# Generate change documentation
bait-report 8id-bits --change-plan "$COMPONENT" --description "$CHANGE_DESC"

# Create deployment checklist
bait-query 8id-bits "Create a deployment checklist for updating $COMPONENT"
```

## Phase 3: Claude Code Integration

### Setup MCP Server

#### Start bAIt MCP Server
```bash
# Start server for specific deployment
bait-mcp-server --deployment 8id-bits --port 8000

# Or start with auto-discovery
bait-mcp-server --auto-discover
```

#### Configure Claude Code
Add to Claude Code MCP settings:
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

### Usage with Claude Code

#### Basic Queries
```
Human: @bait what IOCs are configured for the 8-ID beamline?

Claude: I'll check the 8-ID beamline configuration...
[Uses bAIt MCP tools to query deployment]

The 8-ID beamline has 3 IOCs configured:
1. motor_ioc: Motor control IOC
2. detector_ioc: Detector control IOC  
3. scaler_ioc: Scaler and counter IOC

Each IOC has specific database files and startup configurations.
```

#### Advanced Analysis
```
Human: @bait analyze the detector setup and identify any potential issues

Claude: I'll perform a comprehensive analysis of the detector setup...
[Uses bAIt analysis tools]

Analysis Results:
- 2 detectors configured (Lambda, Pilatus)
- Issue detected: detector_ioc firmware outdated
- Recommendation: Update firmware before next experiment
- Dependencies: 3 MEDM screens, 2 Bluesky devices affected
```

## Phase 4: Operational Procedures

### Regular Maintenance

#### Weekly System Review
```bash
#!/bin/bash
# weekly-review.sh

echo "=== Weekly bAIt System Review ==="
date
echo

# Comprehensive analysis
bait-analyze 8id-bits --comprehensive

# Generate weekly report
bait-report 8id-bits --format weekly --email

# Update knowledge base
bait-build-knowledge 8id-bits

# Check for system updates
bait-query 8id-bits "What maintenance is recommended?"
```

#### Monthly Health Check
```bash
#!/bin/bash
# monthly-health.sh

echo "=== Monthly System Health Check ==="
date
echo

# Full system analysis
bait-analyze 8id-bits --full-analysis

# Performance analysis
bait-query 8id-bits "Analyze system performance trends"

# Generate health report
bait-report 8id-bits --format health --period monthly

# Archive old reports
mkdir -p reports/archive/$(date +%Y%m)
mv reports/daily-*.html reports/archive/$(date +%Y%m)/
```

### Training New Staff

#### Generate Training Materials
```bash
# Create system overview presentation
bait-visualize 8id-bits --type overview --format presentation --output training/

# Generate interactive system tour
bait-report 8id-bits --format training-guide --interactive

# Create troubleshooting guide
bait-report 8id-bits --format troubleshooting-guide
```

#### Interactive Training Session
```bash
# Start interactive session
bait-query 8id-bits --interactive

# Example training queries:
# "Give me a tour of the 8-ID beamline systems"
# "Explain how the detector system works"
# "What are common troubleshooting procedures?"
# "Show me the relationship between IOCs and Bluesky devices"
```

## Deployment Verification

### Verification Checklist

#### ✅ Initial Setup Verification
- [ ] bAIt installed and version confirmed
- [ ] Deployment configuration created
- [ ] Repository access verified
- [ ] Initial analysis completed successfully
- [ ] Basic queries working

#### ✅ Integration Verification
- [ ] Daily check script working
- [ ] Troubleshooting workflow tested
- [ ] Claude Code integration functional
- [ ] MCP server responding
- [ ] Reports generating correctly

#### ✅ Operational Verification
- [ ] Staff trained on basic usage
- [ ] Maintenance procedures documented
- [ ] Emergency procedures tested
- [ ] Performance benchmarks established
- [ ] Success metrics defined

### Performance Benchmarks

#### Analysis Performance
- **Initial Analysis**: < 5 minutes for typical deployment
- **Query Response**: < 30 seconds for standard queries
- **Visualization Generation**: < 2 minutes for complex diagrams
- **Report Generation**: < 1 minute for standard reports

#### Accuracy Metrics
- **Component Detection**: > 95% accuracy
- **Dependency Mapping**: > 90% accuracy
- **Issue Identification**: > 85% accuracy
- **Recommendation Quality**: Staff satisfaction > 80%

## Troubleshooting Deployment Issues

### Common Issues and Solutions

#### Repository Access Issues
**Problem**: Can't access IOC/BITS repositories
**Solution**:
1. Verify SSH keys: `ssh -T git@github.com`
2. Check repository URLs in config.json
3. Verify network connectivity
4. Update authentication tokens

#### Analysis Failures
**Problem**: Analysis fails or returns incomplete results
**Solution**:
1. Check log files: `tail -f ~/.bait/logs/analysis.log`
2. Verify file permissions on local paths
3. Check repository synchronization
4. Run analysis with debug mode: `bait-analyze --debug`

#### Performance Issues
**Problem**: Analysis takes too long or uses too much memory
**Solution**:
1. Enable caching: Set `"cache_results": true` in config
2. Limit analysis scope: Use `--focus` parameters
3. Increase system resources
4. Run analysis during off-peak hours

#### Integration Issues
**Problem**: Claude Code integration not working
**Solution**:
1. Verify MCP server is running: `ps aux | grep bait-mcp`
2. Check MCP server logs: `tail -f ~/.bait/logs/mcp.log`
3. Verify Claude Code MCP configuration
4. Test MCP connection: `bait-mcp-test`

## Success Metrics

### Deployment Success Indicators
- **Time to First Analysis**: < 30 minutes from installation
- **Configuration Accuracy**: > 95% of components detected
- **Staff Adoption**: > 80% of staff using within 2 weeks
- **Query Success Rate**: > 90% of queries answered satisfactorily

### Operational Success Indicators
- **Troubleshooting Efficiency**: 50% reduction in problem resolution time
- **Documentation Quality**: Always current system documentation
- **Training Effectiveness**: 60% reduction in new staff onboarding time
- **System Understanding**: Improved staff confidence scores

## Support and Resources

### Documentation
- **User Guide**: `/bait_base/docs/user-guide.md`
- **API Reference**: `/bait_base/docs/api/`
- **Troubleshooting**: `/bait_base/docs/troubleshooting.md`

### Support Channels
- **GitHub Issues**: https://github.com/ravescovi/bAIt/issues
- **Documentation**: https://bait.readthedocs.io
- **Community**: https://github.com/ravescovi/bAIt/discussions

### Training Resources
- **Video Tutorials**: Coming soon
- **Example Configurations**: `/bait_deployments/examples/`
- **Best Practices**: `/bait_base/docs/best-practices.md`

This deployment guide ensures successful bAIt implementation at any beamline facility with minimal disruption to existing operations.