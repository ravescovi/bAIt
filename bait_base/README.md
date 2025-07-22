# bAIt (Bluesky AI Tools) - Analysis Framework

bAIt is an AI-powered analysis and intelligence system for Bluesky-based data acquisition instruments. It provides comprehensive analysis capabilities for deployment configurations, intelligent querying, and visualization tools.

## Key Features

- **Deployment Analysis**: Comprehensive analysis of IOCs, Bluesky configurations, MEDM screens, and network topology
- **AI-Powered Intelligence**: Specialized AI agents for troubleshooting, optimization, and documentation
- **Natural Language Querying**: Ask questions about your deployment in natural language
- **Automated Visualization**: Generate deployment diagrams, dependency graphs, and system overviews
- **MCP Integration**: Native Claude Code integration for AI-assisted analysis
- **RAG Knowledge System**: Intelligent retrieval and context-aware responses

## Installation

### Development Installation

```bash
cd bait_base/
pip install -e ".[dev]"
```

### Production Installation

```bash
pip install bait
```

## Quick Start

### 1. Configure a Deployment

Create a deployment configuration in `../bait_deployments/`:

```bash
bait-create-deployment my-beamline
```

Edit the configuration file:

```bash
vim ../bait_deployments/my-beamline/config.json
```

### 2. Analyze the Deployment

```bash
bait-analyze my-beamline
```

### 3. Query the Deployment

```bash
bait-query my-beamline "What IOCs are configured?"
bait-query my-beamline "Show me the motor control setup"
```

### 4. Generate Visualizations

```bash
bait-visualize my-beamline --type network
bait-visualize my-beamline --type dependencies --format interactive
```

## Architecture

### Core Components

- **`analyzers/`**: Analysis engines for different component types
- **`agents/`**: AI agents for specialized analysis tasks
- **`MCP/`**: Model Context Protocol integration for Claude Code
- **`knowledge/`**: RAG knowledge system for intelligent querying
- **`visualization/`**: Tools for generating diagrams and visualizations

### Analysis Flow

1. **Configuration Loading**: Load deployment configuration from JSON
2. **Data Collection**: Gather data from IOCs, BITS deployments, MEDM screens
3. **Analysis**: Run specialized analyzers on each component type
4. **Knowledge Building**: Process data into searchable knowledge base
5. **Query Processing**: Handle natural language queries with AI agents
6. **Visualization**: Generate interactive and static visualizations
7. **Reporting**: Create comprehensive analysis reports

## Command Line Interface

### Analysis Commands

```bash
# Analyze a deployment
bait-analyze [deployment-name]

# Generate analysis report
bait-report [deployment-name]

# Validate deployment configuration
bait-validate [deployment-name]
```

### Query Commands

```bash
# Interactive query mode
bait-query [deployment-name]

# Direct query
bait-query [deployment-name] "What IOCs are running?"

# Query with specific context
bait-query [deployment-name] "Troubleshoot detector issues" --context troubleshooting
```

### Visualization Commands

```bash
# Generate network topology
bait-visualize [deployment-name] --type network --format svg

# Generate dependency graph
bait-visualize [deployment-name] --type dependencies --format interactive

# Generate system overview
bait-visualize [deployment-name] --type overview --format pdf
```

### Knowledge System Commands

```bash
# Build knowledge base
bait-build-knowledge [deployment-name]

# Update embeddings
bait-update-embeddings [deployment-name]

# Test retrieval
bait-test-retrieval [deployment-name] "sample query"
```

## MCP Integration

bAIt provides MCP servers for Claude Code integration:

```bash
# Start MCP server
bait-mcp-server

# Available MCP servers:
# - bait_analysis_server: Main analysis capabilities
# - deployment_query_server: Deployment-specific querying
# - troubleshooting_server: Problem diagnosis
# - visualization_server: Diagram generation
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/ravescovi/bAIt.git
cd bAIt/bait_base/
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest
pytest --cov=bait  # With coverage
```

### Code Quality

```bash
ruff check .        # Linting
ruff format .       # Formatting
mypy .              # Type checking
```

### Building Documentation

```bash
pip install -e ".[doc]"
cd docs/
make html
```

## Extension Points

### Custom Analyzers

Create custom analyzers by extending the base analyzer:

```python
from bait.analyzers.base import BaseAnalyzer

class MyAnalyzer(BaseAnalyzer):
    def analyze(self, config):
        # Custom analysis logic
        return results
```

### Custom Agents

Create custom AI agents:

```python
from bait.agents.framework import BaseAgent

class MyAgent(BaseAgent):
    def process_query(self, query, context):
        # Custom query processing
        return response
```

### Custom Visualizations

Create custom visualization generators:

```python
from bait.visualization.generators import BaseGenerator

class MyGenerator(BaseGenerator):
    def generate(self, data):
        # Custom visualization logic
        return visualization
```

## Configuration

### Deployment Configuration

Each deployment requires a `config.json` file specifying:
- Source repositories (IOCs, BITS, MEDM, docs)
- Network configuration (hosts, services, topology)
- Analysis settings (caching, reporting, alerting)
- Integration settings (MCP servers, monitoring)

### Analysis Settings

Configure analysis behavior:
- **auto_update**: Enable automatic updates
- **cache_results**: Cache analysis results
- **generate_reports**: Generate analysis reports
- **alert_on_issues**: Enable issue alerting

## Troubleshooting

### Common Issues

1. **Repository Access**: Ensure proper SSH keys or access tokens
2. **Path Configuration**: Use absolute paths for local_path settings
3. **Network Configuration**: Verify host IP addresses and port accessibility
4. **Dependency Issues**: Check Python version and package compatibility

### Debug Mode

Enable debug logging:

```bash
export BAIT_LOG_LEVEL=DEBUG
bait-analyze my-beamline
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the ANL Open Source License.

## Support

- **Documentation**: https://bait.readthedocs.io
- **Issues**: https://github.com/ravescovi/bAIt/issues
- **Discussions**: https://github.com/ravescovi/bAIt/discussions

## Acknowledgments

bAIt is developed at the Advanced Photon Source (APS) at Argonne National Laboratory. Special thanks to the Bluesky and EPICS communities for their foundational work.