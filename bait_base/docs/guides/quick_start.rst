.. _quick_start:

bAIt Quick Start Guide
======================

Get your first bAIt deployment analysis running in under 10 minutes. This guide covers essential setup with minimal explanation - see complete guides for detailed information.

Prerequisites
-------------

- Python 3.11+
- Git access to beamline repositories
- Basic familiarity with beamline operations

Step 1: Install bAIt (2 minutes)
--------------------------------

.. code-block:: bash

    # Create environment and install
    conda create -y -n bait_env python=3.11
    conda activate bait_env
    pip install "bait[all]"

    # Verify installation
    python -c "import bait; print('✓ bAIt installed')"
    bait --version

Step 2: Configure Your First Deployment (3 minutes)
----------------------------------------------------

.. code-block:: bash

    # Create deployment configuration
    bait-create-deployment my-beamline
    
    # Edit configuration
    vim bait_deployments/my-beamline/config.json

**Basic Configuration Example:**

.. code-block:: json

    {
        "name": "my-beamline",
        "description": "My beamline deployment",
        "components": {
            "iocs": {
                "repositories": [
                    {
                        "name": "ioc_repo",
                        "type": "git",
                        "url": "https://github.com/beamline/iocs.git",
                        "branch": "main",
                        "local_path": "/path/to/local/iocs"
                    }
                ]
            },
            "bits": {
                "repositories": [
                    {
                        "name": "bits_repo", 
                        "type": "git",
                        "url": "https://github.com/beamline/bits.git",
                        "branch": "main",
                        "local_path": "/path/to/local/bits"
                    }
                ]
            }
        }
    }

Step 3: Run Your First Analysis (2 minutes)
--------------------------------------------

.. code-block:: bash

    # Analyze the deployment
    bait-analyze my-beamline

    # View analysis results
    bait-report my-beamline

**Expected Output:**

.. code-block:: text

    🔍 Analysis Results for my-beamline:
    ═══════════════════════════════════
    
    ✅ IOCs discovered: 5
    ✅ BITS devices mapped: 23
    ✅ MEDM screens found: 12
    ⚠️  Issues detected: 2 minor warnings
    
    📊 Overall health: 94/100 (Excellent)
    🔧 Optimization opportunities: 3

Step 4: Query Your Deployment (1 minute)
-----------------------------------------

.. code-block:: bash

    # Interactive query mode
    bait-query my-beamline

    # Direct queries
    bait-query my-beamline "What IOCs are configured?"
    bait-query my-beamline "Show me the motor setup"
    bait-query my-beamline "List all detectors"

**Example Query Session:**

.. code-block:: text

    $ bait-query my-beamline "What IOCs are running?"
    
    🔍 IOC Configuration Analysis:
    ════════════════════════════
    
    IOC Summary:
    • motor_ioc: 8 motors, ESP301 controller
    • detector_ioc: 2 detectors (Lambda, Pilatus)  
    • vacuum_ioc: 6 gauges, 3 pumps
    • beamline_ioc: Shutters, slits, filters
    • experiment_ioc: Sample environment
    
    Status: All IOCs operational ✅

Step 5: Generate Visualizations (1 minute)
-------------------------------------------

.. code-block:: bash

    # Network topology diagram
    bait-visualize my-beamline --type network --format svg
    
    # System dependency graph  
    bait-visualize my-beamline --type dependencies --format interactive
    
    # Complete system overview
    bait-visualize my-beamline --type overview --format pdf

**Visualization Types:**

- **network**: Network topology and connections
- **dependencies**: Component dependencies and relationships
- **overview**: Complete system architecture
- **flow**: Data and control flow diagrams

Step 6: Optional - Set Up Claude Code Integration (1 minute)
-----------------------------------------------------------

.. code-block:: bash

    # Start MCP server for Claude Code integration
    bait-mcp-server --deployment my-beamline
    
    # Test MCP connection
    curl -X GET http://localhost:8000/health

**Claude Code Configuration:**

.. code-block:: json

    {
        "mcp_servers": {
            "bait": {
                "command": "bait-mcp-server",
                "args": ["--deployment", "my-beamline"]
            }
        }
    }

**Using with Claude Code:**

.. code-block:: text

    Human: @bait analyze my beamline deployment
    
    Claude: I'll analyze your beamline deployment using bAIt...
    
    🔍 Deployment Analysis:
    • IOCs: 5 configured, all operational
    • Devices: 23 Bluesky devices mapped
    • Network: Topology validated
    • Issues: 2 minor configuration warnings
    
    Would you like me to detail the warnings or optimization suggestions?

What You've Accomplished
------------------------

In under 10 minutes, you've:

✅ **Installed bAIt** with full analysis capabilities
✅ **Configured deployment** with repository connections
✅ **Analyzed deployment** with comprehensive health check
✅ **Queried configuration** with natural language interface
✅ **Generated visualizations** of system architecture
✅ **Optional: Set up AI integration** with Claude Code

Next Steps
----------

**Immediate (next 30 minutes):**

1. :doc:`Configure advanced analysis settings <configuration>` - Fine-tune analysis behavior
2. :doc:`Set up multiple deployments <deployment_management>` - Manage multiple beamlines
3. :doc:`Create custom analyzers <analyzers>` - Add specialized analysis capabilities

**Short term (next few hours):**

4. :doc:`Implement automated monitoring <monitoring>` - Continuous health checks
5. :doc:`Set up team collaboration <collaboration>` - Multi-user access and permissions
6. :doc:`Configure alerting <alerting>` - Proactive issue detection

**Advanced (next few days):**

7. :doc:`Develop custom AI agents <agents>` - Specialized troubleshooting agents
8. :doc:`Create custom visualizations <visualizations>` - Tailored diagrams and reports
9. :doc:`Integration workflows <workflows>` - Automated analysis and reporting pipelines

Common First Issues and Solutions
---------------------------------

**Problem: Repository access denied**

.. code-block:: bash

    # Solution: Set up proper authentication
    git config --global user.name "Your Name"
    git config --global user.email "your.email@lab.gov"
    
    # For SSH keys
    ssh-add ~/.ssh/id_rsa

**Problem: Path not found errors**

.. code-block:: bash

    # Solution: Use absolute paths in config.json
    # Correct: "/home/beamline/iocs"
    # Wrong: "./iocs" or "~/iocs"

**Problem: Analysis returns no results**

.. code-block:: bash

    # Solution: Verify repository structure
    ls -la /path/to/local/iocs  # Should contain IOC directories
    ls -la /path/to/local/bits  # Should contain BITS configuration

**Problem: MCP server won't start**

.. code-block:: bash

    # Solution: Check port availability and permissions
    netstat -tuln | grep 8000
    bait-mcp-server --deployment my-beamline --debug

Getting Help
------------

**Resources:**

- **Documentation**: :doc:`Complete bAIt guides <index>`
- **Examples**: Working examples in `bait_base/docs/examples/`
- **Issues**: Report problems at https://github.com/ravescovi/bAIt/issues  
- **Community**: APS beamline operations and analysis community

**Emergency Debugging Commands:**

.. code-block:: bash

    # Check installation
    python -c "import bait; print(f'bAIt {bait.__version__} installed')"
    
    # Test deployment configuration
    bait-validate my-beamline
    
    # Debug analysis
    bait-analyze my-beamline --debug --verbose
    
    # Check MCP server
    bait-mcp-server --deployment my-beamline --test

**Ready to dive deeper?** Start with :doc:`deployment_management` for comprehensive deployment configuration patterns.