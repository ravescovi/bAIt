.. _deployment_management:

Deployment Management with bAIt
===============================

This comprehensive guide covers bAIt deployment configuration, from simple single-beamline setups to enterprise-scale multi-facility analysis systems.

Quick Start: Create a Deployment in 3 Steps
--------------------------------------------

**Set up deployment analysis in 3 commands:**

.. code-block:: bash

    # 1. Create deployment configuration
    bait-create-deployment my-beamline
    
    # 2. Configure sources (edit the generated config.json)
    vim bait_deployments/my-beamline/config.json
    
    # 3. Run analysis
    bait-analyze my-beamline

**Basic Configuration Example:**

.. code-block:: json

    {
        "name": "my-beamline",
        "components": {
            "iocs": {
                "repositories": [{
                    "name": "ioc_repo",
                    "url": "https://github.com/beamline/iocs.git",
                    "local_path": "/path/to/iocs"
                }]
            }
        }
    }

Complete Deployment Configuration Guide
---------------------------------------

Understanding bAIt Deployment Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

bAIt deployments follow a multi-component analysis architecture:

1. **Configuration Layer** - JSON files defining data sources and analysis settings
2. **Data Collection Layer** - Automated gathering from repositories and live systems
3. **Analysis Layer** - Specialized analyzers for each component type
4. **Intelligence Layer** - AI agents for querying and troubleshooting
5. **Visualization Layer** - Automated generation of diagrams and reports

**Deployment Structure:**

.. code-block:: text

    bait_deployments/
    ├── my-beamline/                    # Deployment directory
    │   ├── config.json                 # Main configuration
    │   ├── analysis_cache/             # Cached analysis results
    │   ├── reports/                    # Generated reports
    │   ├── visualizations/             # Generated diagrams
    │   └── custom_configs/             # Custom analyzer settings
    └── another-beamline/               # Another deployment
        └── ...

Deployment Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Single Beamline Configuration:**

.. code-block:: json

    {
        "name": "8id-bits",
        "description": "8-ID beamline analysis deployment", 
        "type": "single_beamline",
        "components": {
            "iocs": {
                "repositories": [
                    {
                        "name": "8id_iocs",
                        "type": "git",
                        "url": "https://github.com/APS-8ID/iocs.git",
                        "branch": "main",
                        "local_path": "/home/8id/iocs",
                        "analysis_enabled": true
                    }
                ]
            },
            "bits": {
                "repositories": [
                    {
                        "name": "8id_bits",
                        "type": "git", 
                        "url": "https://github.com/APS-8ID/8id-bits.git",
                        "branch": "main",
                        "local_path": "/home/8id/bits",
                        "startup_script": "src/8id_bits/startup.py"
                    }
                ]
            },
            "medm": {
                "directories": [
                    "/home/8id/medm/screens",
                    "/opt/synApps/support/medm/8id"
                ],
                "file_patterns": ["*.adl", "*.opi", "*.ui"]
            },
            "documentation": {
                "repositories": [
                    {
                        "name": "8id_docs",
                        "type": "git",
                        "url": "https://github.com/APS-8ID/documentation.git",
                        "branch": "main",
                        "local_path": "/home/8id/docs"
                    }
                ]
            }
        },
        "network": {
            "hosts": [
                {"name": "8idioc1", "ip": "164.54.160.101", "role": "ioc_host"},
                {"name": "8idioc2", "ip": "164.54.160.102", "role": "ioc_host"},
                {"name": "8idws1", "ip": "164.54.160.103", "role": "workstation"}
            ],
            "services": [
                {"name": "archiver", "port": 17665, "host": "8idioc1"},
                {"name": "gateway", "port": 5064, "host": "8idioc1"}
            ]
        },
        "analysis_settings": {
            "auto_update": true,
            "cache_results": true,
            "generate_reports": true,
            "report_schedule": "daily",
            "alert_on_issues": true
        }
    }

**Multi-Beamline Configuration:**

.. code-block:: json

    {
        "name": "aps-sector12",
        "description": "APS Sector 12 multi-beamline analysis",
        "type": "multi_beamline",
        "beamlines": ["12id-b", "12id-c", "12id-d"],
        "components": {
            "iocs": {
                "repositories": [
                    {
                        "name": "12id_common_iocs",
                        "url": "https://github.com/APS-12ID/common-iocs.git",
                        "local_path": "/net/s12dserv/xorApps/iocs",
                        "subdirectories": {
                            "12id-b": "12idb/iocs/", 
                            "12id-c": "12idc/iocs/",
                            "12id-d": "12idd/iocs/"
                        }
                    }
                ]
            },
            "bits": {
                "repositories": [
                    {
                        "name": "12id_bits",
                        "url": "https://github.com/APS-12ID/12id-bits.git",
                        "local_path": "/net/s12dserv/xorApps/bits",
                        "beamline_configs": {
                            "12id-b": "src/id12b_bits/",
                            "12id-c": "src/id12c_bits/", 
                            "12id-d": "src/id12d_bits/"
                        }
                    }
                ]
            },
            "shared_components": {
                "common_devices": "/net/s12dserv/xorApps/common/devices/",
                "shared_plans": "/net/s12dserv/xorApps/common/plans/",
                "utilities": "/net/s12dserv/xorApps/common/utils/"
            }
        },
        "network": {
            "domain": "aps.anl.gov",
            "subnet": "164.54.160.0/24",
            "shared_services": [
                {"name": "data_management", "host": "s12dserv", "port": 5432},
                {"name": "archiver", "host": "s12arch", "port": 17665}
            ]
        }
    }

**Enterprise Configuration:**

.. code-block:: json

    {
        "name": "aps-facility",
        "description": "APS facility-wide analysis system",
        "type": "enterprise",
        "scope": "facility_wide", 
        "sectors": [1, 2, 3, 8, 9, 12, 15, 16, 20, 26, 32, 34],
        "components": {
            "central_repositories": {
                "apstools": {
                    "url": "https://github.com/BCDA-APS/apstools.git",
                    "role": "shared_library"
                },
                "bits": {
                    "url": "https://github.com/BCDA-APS/BITS.git", 
                    "role": "framework"
                },
                "common_iocs": {
                    "url": "https://github.com/APS-Operations/common-iocs.git",
                    "role": "shared_iocs"
                }
            },
            "beamline_configs": {
                "discovery_method": "automatic",
                "config_server": "https://aps-config.anl.gov/api",
                "update_schedule": "hourly"
            }
        },
        "analysis_infrastructure": {
            "distributed_analysis": true,
            "worker_nodes": ["aps-analysis-1", "aps-analysis-2", "aps-analysis-3"],
            "database": {
                "type": "postgresql",
                "host": "aps-db.anl.gov",
                "database": "aps_analysis"
            },
            "caching": {
                "type": "redis",
                "cluster": ["redis-1.aps.anl.gov", "redis-2.aps.anl.gov"]
            }
        }
    }

Repository Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Git Repository Configuration:**

.. code-block:: json

    {
        "repositories": [
            {
                "name": "beamline_iocs",
                "type": "git",
                "url": "https://github.com/beamline/iocs.git",
                "branch": "main",
                "local_path": "/home/beamline/iocs",
                "authentication": {
                    "method": "ssh_key",
                    "key_path": "~/.ssh/id_rsa"
                },
                "update_policy": {
                    "automatic": true,
                    "schedule": "0 */6 * * *",  # Every 6 hours
                    "conflict_resolution": "pull_rebase"
                },
                "analysis_config": {
                    "enabled": true,
                    "include_patterns": ["*.cmd", "*.db", "*.template"],
                    "exclude_patterns": ["*.bak", "*.tmp", "*~"],
                    "depth": "full_history"
                }
            }
        ]
    }

**Local Directory Configuration:**

.. code-block:: json

    {
        "components": {
            "medm": {
                "directories": [
                    {
                        "path": "/home/beamline/medm",
                        "recursive": true,
                        "file_patterns": ["*.adl", "*.opi"],
                        "watch_for_changes": true,
                        "metadata": {
                            "category": "operator_screens",
                            "maintainer": "beamline_team"
                        }
                    }
                ]
            },
            "data_storage": {
                "directories": [
                    {
                        "path": "/data/beamline",
                        "monitor_usage": true,
                        "alert_threshold": "90%",
                        "cleanup_policy": {
                            "enabled": true,
                            "retention_days": 30
                        }
                    }
                ]
            }
        }
    }

**Network Service Configuration:**

.. code-block:: json

    {
        "network": {
            "discovery": {
                "enabled": true,
                "methods": ["nmap", "epics_ca", "service_registry"]
            },
            "hosts": [
                {
                    "name": "ioc_host_1",
                    "ip": "164.54.160.101",
                    "role": "ioc_host",
                    "services": ["epics_ca", "ssh", "http"],
                    "monitoring": {
                        "ping": true,
                        "port_scan": [22, 80, 5064, 5065],
                        "resource_monitoring": true
                    }
                }
            ],
            "topology_mapping": {
                "enabled": true,
                "map_switches": true,
                "trace_connections": true
            }
        }
    }

Advanced Configuration Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Analysis Pipeline Configuration:**

.. code-block:: json

    {
        "analysis_pipeline": {
            "stages": [
                {
                    "name": "data_collection",
                    "analyzers": ["ioc_analyzer", "bits_analyzer"],
                    "parallel": true,
                    "timeout": 300
                },
                {
                    "name": "cross_validation", 
                    "analyzers": ["integrity_analyzer", "consistency_analyzer"],
                    "depends_on": ["data_collection"],
                    "parallel": false
                },
                {
                    "name": "intelligence_analysis",
                    "analyzers": ["pattern_analyzer", "optimization_analyzer"],
                    "depends_on": ["cross_validation"],
                    "ai_enabled": true
                }
            ],
            "failure_handling": {
                "continue_on_error": true,
                "retry_attempts": 3,
                "retry_delay": 30
            }
        }
    }

**AI Agent Configuration:**

.. code-block:: json

    {
        "ai_agents": {
            "troubleshooting_agent": {
                "enabled": true,
                "model": "claude-3-sonnet",
                "specialization": "beamline_operations",
                "knowledge_base": {
                    "include_manuals": true,
                    "include_procedures": true,
                    "include_history": 90  # days
                },
                "capabilities": [
                    "issue_diagnosis",
                    "solution_recommendations", 
                    "procedure_guidance"
                ]
            },
            "optimization_agent": {
                "enabled": true,
                "model": "claude-3-haiku",
                "specialization": "performance_optimization",
                "analysis_focus": [
                    "configuration_efficiency",
                    "resource_utilization",
                    "workflow_optimization"
                ]
            }
        }
    }

**Monitoring and Alerting Configuration:**

.. code-block:: json

    {
        "monitoring": {
            "health_checks": {
                "schedule": "*/15 * * * *",  # Every 15 minutes
                "checks": [
                    "repository_accessibility",
                    "service_availability", 
                    "disk_usage",
                    "configuration_consistency"
                ]
            },
            "alerting": {
                "enabled": true,
                "channels": [
                    {
                        "type": "email",
                        "recipients": ["beamline-ops@lab.gov"],
                        "severity": ["critical", "high"]
                    },
                    {
                        "type": "slack",
                        "webhook": "https://hooks.slack.com/...",
                        "severity": ["critical", "high", "medium"]
                    }
                ],
                "rules": [
                    {
                        "condition": "ioc_down",
                        "severity": "critical",
                        "message": "IOC {{ioc_name}} is not responding"
                    },
                    {
                        "condition": "configuration_drift",
                        "severity": "medium",
                        "message": "Configuration changes detected in {{component}}"
                    }
                ]
            }
        }
    }

Environment-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Production Environment:**

.. code-block:: json

    {
        "environment": "production",
        "analysis_settings": {
            "cache_results": true,
            "cache_duration": 3600,  # 1 hour
            "generate_reports": true,
            "auto_update": true,
            "parallel_analysis": true,
            "worker_count": 4
        },
        "security": {
            "authentication_required": true,
            "authorization_enabled": true,
            "audit_logging": true,
            "encrypted_storage": true
        },
        "performance": {
            "optimize_for": "accuracy",
            "memory_limit": "4G",
            "timeout": 1800  # 30 minutes
        }
    }

**Development Environment:**

.. code-block:: json

    {
        "environment": "development",
        "analysis_settings": {
            "cache_results": false,
            "generate_reports": false,
            "auto_update": false,
            "debug_mode": true,
            "verbose_logging": true
        },
        "security": {
            "authentication_required": false,
            "audit_logging": false
        },
        "performance": {
            "optimize_for": "speed",
            "memory_limit": "2G",
            "timeout": 300  # 5 minutes
        }
    }

Deployment Management Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Basic Deployment Operations:**

.. code-block:: bash

    # Create new deployment
    bait-create-deployment my-beamline
    
    # List all deployments
    bait-list-deployments
    
    # Show deployment status
    bait-status my-beamline
    
    # Validate deployment configuration
    bait-validate my-beamline
    
    # Update deployment from repositories  
    bait-update-deployment my-beamline
    
    # Remove deployment (with confirmation)
    bait-remove-deployment my-beamline

**Advanced Management Operations:**

.. code-block:: bash

    # Clone deployment configuration
    bait-clone-deployment source-beamline new-beamline
    
    # Synchronize deployments
    bait-sync-deployments --source production --target staging
    
    # Backup deployment configuration and data
    bait-backup-deployment my-beamline --include-cache
    
    # Restore deployment from backup
    bait-restore-deployment my-beamline backup-file.tar.gz
    
    # Export deployment configuration  
    bait-export-deployment my-beamline --format yaml
    
    # Import deployment configuration
    bait-import-deployment config-file.yaml

**Batch Operations:**

.. code-block:: bash

    # Analyze multiple deployments
    bait-analyze-batch 8id-bits 12id-bits 16bm-bits --parallel
    
    # Update multiple deployments
    bait-update-batch --pattern "*-bits" --exclude test-*
    
    # Generate reports for all deployments
    bait-report-batch --format pdf --output-dir /reports
    
    # Health check all deployments
    bait-health-check-all --format summary

Configuration Validation and Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration Validation:**

.. code-block:: bash

    # Validate configuration syntax
    bait-validate my-beamline --check-syntax
    
    # Validate repository access
    bait-validate my-beamline --check-repositories
    
    # Validate network configuration
    bait-validate my-beamline --check-network
    
    # Comprehensive validation
    bait-validate my-beamline --comprehensive

**Testing Configuration Changes:**

.. code-block:: bash

    # Test configuration changes without applying
    bait-test-config my-beamline --dry-run
    
    # Test with simulated data
    bait-test-config my-beamline --simulate
    
    # Test specific components
    bait-test-config my-beamline --components iocs,bits
    
    # Performance test configuration
    bait-test-config my-beamline --benchmark

Migration and Upgrade Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Migrating from Legacy Systems:**

.. code-block:: python

    # utils/migration.py - Migration utilities
    from bait.config import DeploymentConfig
    from bait.migration import LegacyConfigMigrator
    
    def migrate_legacy_config(legacy_path, new_deployment_name):
        """Migrate legacy configuration to bAIt format."""
        
        migrator = LegacyConfigMigrator()
        
        # Load legacy configuration
        legacy_config = migrator.load_legacy(legacy_path)
        
        # Convert to bAIt format
        bait_config = migrator.convert_to_bait(legacy_config)
        
        # Validate migrated configuration
        if migrator.validate_migration(bait_config):
            # Save new deployment
            deployment = DeploymentConfig(new_deployment_name)
            deployment.save_config(bait_config)
            return True
        else:
            return False

**Configuration Schema Evolution:**

.. code-block:: python

    # Handle configuration schema changes
    from bait.config.schema import ConfigSchemaUpgrader
    
    def upgrade_deployment_config(deployment_name):
        """Upgrade deployment to latest schema version."""
        
        upgrader = ConfigSchemaUpgrader()
        
        # Load current configuration
        current_config = upgrader.load_config(deployment_name)
        current_version = upgrader.detect_version(current_config)
        
        # Upgrade to latest version
        if upgrader.needs_upgrade(current_version):
            upgraded_config = upgrader.upgrade(
                current_config, 
                from_version=current_version,
                to_version="latest"
            )
            
            # Save upgraded configuration
            upgrader.save_config(deployment_name, upgraded_config)
            return True
        
        return False

Best Practices and Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration Organization:**

.. code-block:: text

    bait_deployments/
    ├── production/              # Production deployments
    │   ├── 8id-bits/
    │   ├── 12id-bits/
    │   └── 16bm-bits/
    ├── staging/                 # Staging/test deployments
    │   ├── test-8id/
    │   └── test-12id/
    ├── templates/               # Configuration templates
    │   ├── single-beamline.json
    │   ├── multi-beamline.json
    │   └── enterprise.json
    └── shared/                  # Shared configurations
        ├── common-settings.json
        └── network-configs.json

**DO:**

- Use absolute paths for all file and directory references
- Implement proper authentication and authorization
- Validate configurations before deployment
- Use version control for configuration files
- Monitor repository access and update schedules
- Document custom configurations and modifications
- Test configuration changes in staging environments
- Implement backup and disaster recovery procedures

**DON'T:**

- Use relative paths in configuration files
- Store credentials or secrets in configuration files
- Skip validation of configuration changes
- Modify production configurations without testing
- Ignore repository authentication and access errors
- Mix development and production configurations
- Deploy without proper backup procedures

**Security Considerations:**

- Store sensitive information in secure credential stores
- Use SSH keys or tokens for repository authentication
- Implement role-based access controls for deployments
- Enable audit logging for configuration changes
- Encrypt sensitive configuration data at rest
- Restrict network access to analysis systems
- Regularly rotate authentication credentials

**Performance Optimization:**

- Configure appropriate caching for your environment
- Use parallel analysis for large deployments
- Optimize repository update schedules
- Monitor system resource usage
- Implement intelligent retry and timeout policies
- Use distributed analysis for enterprise deployments

**Next Steps:**

1. :doc:`Run comprehensive analysis <analysis>` on your configured deployment
2. :doc:`Set up monitoring and alerting <monitoring>` for continuous health checks
3. :doc:`Configure AI agents <agents>` for intelligent troubleshooting and optimization
4. :doc:`Implement team collaboration <collaboration>` for multi-user environments