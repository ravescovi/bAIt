# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains **bAIt** (Bluesky AI Tools), an AI-powered analysis and intelligence system for Bluesky-based data acquisition instruments at the Advanced Photon Source (APS) at Argonne National Laboratory.

**Key Scope**: bAIt is a **separate analysis package** that analyzes existing deployments and answers questions about them. It does **NOT control** any hardware or systems.

### Repository Structure

The repository is organized into two main sections:

- **`bait_base/`**: Core bAIt analysis tools and framework
  - `analyzers/` - Analysis engines for different components
  - `agents/` - AI agents for specialized analysis tasks
  - `MCP/` - Model Context Protocol servers for Claude Code integration
  - `knowledge/` - RAG knowledge system for intelligent querying
  - `visualization/` - Tools for generating system diagrams and visualizations
  - `docs/` - bAIt framework documentation

- **`bait_deployments/`**: Deployment-specific configurations
  - Each folder corresponds to a specific beamline deployment
  - Contains configuration files pointing to IOCs, BITS deployments, MEDM screens
  - Includes repository references, branches, and local paths

- **`bits_base/`**: Legacy foundation packages (maintained for reference)
  - `BITS/` - Main apsbits package with instrument templates and framework
  - `apstools/` - Library of Python tools for Bluesky Framework at APS
  - `guarneri/` - Instrument configuration management
  - `BITS-Starter/` - Template for creating new instruments

- **`bits_deployments/`**: Legacy specific instrument deployments (maintained for reference)
  - Various beamline-specific instruments (8id-bits, 9id_bits, 12id-bits, etc.)
  - Each deployment contains startup scripts, configurations, and queueserver setups

## Development Commands

### bAIt Core Development (bait_base/)

**Build and Install:**
```bash
# Install bAIt analysis framework
cd bait_base/
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

**Testing:**
```bash
# Run tests using pytest
pytest

# Run tests with coverage
pytest --cov=bait_base/
```

**Code Quality:**
```bash
# Format code with ruff
ruff format .

# Lint with ruff
ruff check .

# Fix linting issues
ruff check --fix .
```

### bAIt Analysis Commands

**Deployment Analysis:**
```bash
# Analyze a specific deployment
bait-analyze [deployment-name]

# Generate deployment report
bait-report [deployment-name]

# Validate deployment configuration
bait-validate [deployment-name]
```

**Query Interface:**
```bash
# Interactive query mode
bait-query [deployment-name]

# Direct query
bait-query [deployment-name] "What IOCs are running?"

# Generate visualization
bait-visualize [deployment-name] --type network
```

### Deployment Configuration

**Create New Deployment Configuration:**
```bash
# Create new deployment configuration
bait-create-deployment [deployment-name]

# Update deployment from repositories
bait-update-deployment [deployment-name]

# Sync deployment data
bait-sync [deployment-name]
```

### MCP and AI Integration

**MCP Server Operations:**
```bash
# Start bAIt MCP server
cd bait_base/MCP/
python -m bait_mcp_server

# Test MCP server connections
mcp-test bait-analysis-server
```

**AI Agent Development:**
```bash
# Configure AI agents and personas
cd bait_base/agents/personas/
# Edit persona configurations
vim [persona-name].yaml

# Test agent behaviors
python -m bait_base.agents.test_agent [persona-name]
```

### Knowledge System

**RAG System Operations:**
```bash
# Build knowledge base for deployment
bait-build-knowledge [deployment-name]

# Update embeddings
bait-update-embeddings [deployment-name]

# Test retrieval
bait-test-retrieval [deployment-name] "sample query"
```

### Visualization

**Generate Diagrams:**
```bash
# Generate network topology
bait-visualize [deployment-name] --type network --format svg

# Generate dependency graph
bait-visualize [deployment-name] --type dependencies --format interactive

# Generate system overview
bait-visualize [deployment-name] --type overview --format pdf
```

### Legacy System Commands (bits_base/)

**Core Package Development:**
```bash
# For any package in bits_base/
cd bits_base/[package_name]
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

**Instrument Commands:**
```bash
# Create new instrument (legacy)
bits-create [instrument_name]

# Run instrument startup module
bits-run [package_name]

# Delete an instrument
bits-delete [instrument_name]
```

## Architecture

### bAIt Analysis Framework

bAIt provides a comprehensive analysis and intelligence system for Bluesky-based deployments:

- **Analysis Engine**: Multi-component analyzers for IOCs, Bluesky configurations, MEDM screens, and network topology
- **AI Agent System**: Specialized agents for different analysis tasks (troubleshooting, optimization, documentation)
- **Knowledge System**: RAG-based knowledge base for intelligent querying and context-aware responses
- **Visualization Tools**: Automated generation of deployment diagrams, dependency graphs, and system overviews
- **MCP Integration**: Native Claude Code integration for AI-assisted deployment analysis

### Core Analysis Components

**Deployment Analysis:**
- **IOC Analyzer**: Parses IOC configurations, extracts PV lists, validates dependencies
- **Bluesky Analyzer**: Analyzes device mappings, plan configurations, and startup sequences
- **MEDM Analyzer**: Parses MEDM screens, validates PV connections, maps control relationships
- **Network Analyzer**: Maps network topology, validates service endpoints
- **Integrity Analyzer**: Checks consistency across all components

**AI Intelligence Layer:**
- **Query Processing**: Natural language queries about deployment configurations
- **Problem Diagnosis**: AI-powered troubleshooting and issue identification
- **Optimization Recommendations**: Performance and configuration improvement suggestions
- **Documentation Generation**: Automated documentation and system diagrams

### Deployment Configuration System

**Configuration Structure:**
- Each deployment has a `config.json` file specifying all component locations
- Repository references with branches and local paths
- Network topology and service definitions
- Analysis settings and caching preferences

**Data Sources:**
- **IOC Repositories**: EPICS IOC configurations and databases
- **BITS Deployments**: Bluesky instrument configurations and startup files
- **MEDM Screens**: Display files and control screen definitions
- **Documentation**: Technical documentation and operational procedures

### Knowledge and Retrieval System

**RAG Architecture:**
- **Multi-Modal Embeddings**: Text, code, configuration files, and documentation
- **Deployment-Specific Knowledge**: Separate knowledge bases for each deployment
- **Semantic Search**: Context-aware retrieval for accurate responses
- **Graph-Based Retrieval**: Relationship-aware information retrieval

**Knowledge Sources:**
- Configuration files (YAML, JSON, IOC databases)
- Source code (Python, startup scripts, plan definitions)
- Documentation (technical docs, operational procedures)
- Historical data (logs, reports, issue tracking)

### Legacy System Integration

**BITS Framework (Legacy):**
- Maintained for reference and backward compatibility
- Standard Bluesky instrument templates and development tools
- Device registries and startup system architectures

### bAIt Deployment Structure

Each bAIt deployment configuration follows this pattern:
```
bait_deployments/[deployment_name]/
├── config.json         # Main deployment configuration
├── analysis_cache/     # Cached analysis results
├── reports/           # Generated reports
└── custom_configs/    # Custom analysis configurations
```

### Key bAIt Components

1. **Deployment Analyzer**: Comprehensive analysis of entire deployment configurations
2. **AI Agent System**: Specialized agents for different analysis tasks
3. **Knowledge Base**: RAG-powered knowledge system for intelligent querying
4. **Visualization Engine**: Automated generation of deployment diagrams and visualizations
5. **MCP Integration**: Native Claude Code integration for AI-assisted analysis
6. **Query Interface**: Natural language querying of deployment configurations
7. **Integrity Checker**: Consistency validation across all deployment components
8. **Report Generator**: Automated generation of deployment analysis reports
9. **Configuration Manager**: Management of deployment configurations and data sources

### Legacy Instrument Structure (Reference)

Each legacy instrument deployment follows this pattern:
```
src/[instrument_name]/
├── startup.py          # Main startup module
├── configs/            # Configuration files
│   ├── iconfig.yml     # Main instrument configuration
│   └── devices.yml     # Device definitions
├── devices/            # Custom device implementations
├── plans/              # Custom scan plans
├── callbacks/          # Data writing callbacks
├── suspenders/         # Suspender implementations
└── utils/              # Utility functions
```

### Testing Strategy

- Unit tests for core functionality using pytest
- Mock-based testing for EPICS devices using `pytest-mock`
- Test configuration in `pyproject.toml` with import mode set to `importlib`
- Integration tests for instrument startup sequences

## Package Dependencies

### Core Dependencies
- **bluesky**: Event-driven data collection framework
- **ophyd**: Hardware abstraction layer for EPICS
- **databroker**: Data cataloging and retrieval
- **apstools**: APS-specific utilities and devices

### Development Dependencies
- **pytest**: Testing framework
- **ruff**: Code formatting and linting
- **mypy**: Static type checking
- **pre-commit**: Git hook management

## Configuration Management

### Instrument Configuration (iconfig.yml)
Central configuration file containing:
- Data management settings
- Catalog configuration
- Callback settings (NeXus, SPEC)
- Logging configuration

### Device Configuration (devices.yml)
YAML files defining:
- Device instantiation parameters
- EPICS PV mappings
- Device labels and metadata
- Environment-specific overrides

### Environment Detection
The framework automatically detects if running:
- On APS subnet (loads additional device configurations)
- In queueserver mode (imports specific plan sets)
- In development vs production environments

## Best Practices

### Code Style
- Follow PEP 8 with line length of 88 characters (ruff format)
- Use type hints for function signatures
- Single-line imports enforced by isort configuration

### Testing
- Write unit tests for all new functionality
- Use dependency injection for EPICS connections in tests
- Mock external dependencies appropriately

### Configuration
- Keep environment-specific settings in separate YAML files
- Use device labels consistently across configurations
- Document configuration parameters in YAML comments

### Documentation
- Maintain docstrings for all public APIs
- Use Sphinx for documentation generation
- Include examples in docstrings where appropriate
- **All markdown documentation files (except README.md) must be placed in the docs/ directory**
- No .md files should be created at the repository root level