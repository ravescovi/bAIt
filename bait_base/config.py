"""
Configuration management for bAIt.

This module provides functions for loading, validating, and managing
deployment configurations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class DeploymentMetadata(BaseModel):
    """Deployment metadata structure."""
    name: str = Field(..., description="Deployment name")
    description: str = Field(..., description="Deployment description")
    version: str = Field(default="1.0.0", description="Configuration version")
    beamline: str | None = Field(None, description="Beamline identifier")
    maintainer: str | None = Field(None, description="Maintainer contact")
    created: datetime | None = Field(None, description="Creation timestamp")
    updated: datetime | None = Field(None, description="Last update timestamp")
    sector: str | None = Field(None, description="Sector identifier")
    facility: str | None = Field(None, description="Facility name")
    last_analyzed: str | None = Field(None, description="Last analysis timestamp")
    contact: str | None = Field(None, description="Contact information")

    class Config:
        extra = "allow"  # Allow extra fields


class SourceConfig(BaseModel):
    """Source configuration structure."""
    repository: str = Field(..., description="Repository URL")
    branch: str = Field(default="main", description="Branch name")
    local_path: str | None = Field(None, description="Local path")
    enabled: bool = Field(default=True, description="Whether source is enabled")
    type: str | None = Field(None, description="Source type (iocs, bits, medm, docs)")
    description: str | None = Field(None, description="Source description")

    class Config:
        extra = "allow"  # Allow extra fields

    @validator('repository')
    def validate_repository(cls, v):
        if not v.startswith(('http://', 'https://', 'git@', 'file://')):
            raise ValueError('Repository must be a valid URL or path')
        return v


class NetworkConfig(BaseModel):
    """Network configuration structure."""
    hosts: dict[str, Any] | list[dict[str, Any]] | None = Field(None, description="Host configurations")
    services: dict[str, Any] | list[dict[str, Any]] | None = Field(None, description="Service configurations")
    subnet: str | None = Field(None, description="Subnet information")
    domain: str | None = Field(None, description="Network domain")


class AnalysisSettings(BaseModel):
    """Analysis settings structure."""
    auto_update: bool = Field(default=False, description="Enable automatic updates")
    cache_results: bool = Field(default=True, description="Cache analysis results")
    generate_reports: bool = Field(default=True, description="Generate analysis reports")
    alert_on_issues: bool = Field(default=False, description="Enable issue alerting")
    update_interval: int = Field(default=3600, description="Update interval in seconds")
    cache_ttl: int | None = Field(None, description="Cache time-to-live in seconds")
    report_schedule: str | None = Field(None, description="Report generation schedule")
    alert_threshold: str | None = Field(None, description="Alert threshold level")
    enable_visualization: bool | None = Field(None, description="Enable visualization generation")
    visualization_formats: list[str] | None = Field(None, description="Supported visualization formats")


class DeploymentConfig(BaseModel):
    """Complete deployment configuration structure."""
    deployment: DeploymentMetadata = Field(..., description="Deployment metadata")
    sources: dict[str, SourceConfig] = Field(..., description="Source configurations")
    network: NetworkConfig | None = Field(None, description="Network configuration")
    analysis: AnalysisSettings | None = Field(None, description="Analysis settings")
    integrations: dict[str, Any] | None = Field(None, description="Integration configurations")

    class Config:
        extra = "allow"  # Allow extra fields

    @validator('sources')
    def validate_sources(cls, v):
        if not v:
            raise ValueError('At least one source must be configured')
        return v


def load_deployment_config(config_path: str | Path) -> DeploymentConfig:
    """
    Load and validate deployment configuration.

    Args:
        config_path: Path to configuration file

    Returns:
        DeploymentConfig object

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is not valid JSON
        ValueError: If configuration is invalid
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    if not config_path.is_file():
        raise ValueError(f"Configuration path is not a file: {config_path}")

    try:
        with open(config_path) as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in configuration file: {e}")

    # Convert sources to SourceConfig objects
    if 'sources' in config_data:
        sources = {}
        for source_name, source_data in config_data['sources'].items():
            sources[source_name] = SourceConfig(**source_data)
        config_data['sources'] = sources

    # Convert network to NetworkConfig if present
    if 'network' in config_data:
        config_data['network'] = NetworkConfig(**config_data['network'])

    # Convert analysis to AnalysisSettings if present
    if 'analysis' in config_data:
        config_data['analysis'] = AnalysisSettings(**config_data['analysis'])
    elif 'analysis_settings' in config_data:
        config_data['analysis'] = AnalysisSettings(**config_data['analysis_settings'])
        # Remove the old key
        del config_data['analysis_settings']

    # Convert deployment to DeploymentMetadata
    if 'deployment' in config_data:
        config_data['deployment'] = DeploymentMetadata(**config_data['deployment'])

    return DeploymentConfig(**config_data)


def find_deployment_config(deployment_name: str, base_path: Path | None = None) -> Path | None:
    """
    Find deployment configuration file.

    Args:
        deployment_name: Name of the deployment
        base_path: Base path to search (defaults to bait_deployments)

    Returns:
        Path to config file if found, None otherwise
    """
    if base_path is None:
        base_path = Path("bait_deployments")

    # Try direct path
    deployment_path = base_path / deployment_name
    config_path = deployment_path / "config.json"

    if config_path.exists():
        return config_path

    # Try searching in subdirectories
    if base_path.exists():
        for item in base_path.iterdir():
            if item.is_dir() and item.name == deployment_name:
                config_path = item / "config.json"
                if config_path.exists():
                    return config_path

    return None


def validate_deployment_config(config: DeploymentConfig) -> list[str]:
    """
    Validate deployment configuration and return list of issues.

    Args:
        config: Deployment configuration to validate

    Returns:
        List of validation issues (empty if valid)
    """
    issues = []

    # Check deployment metadata
    if not config.deployment.name:
        issues.append("Deployment name is required")

    if not config.deployment.description:
        issues.append("Deployment description is required")

    # Check sources
    if not config.sources:
        issues.append("At least one source must be configured")

    for source_name, source_config in config.sources.items():
        if not source_config.repository:
            issues.append(f"Source '{source_name}' is missing repository URL")

        if source_config.local_path and not Path(source_config.local_path).is_absolute():
            issues.append(f"Source '{source_name}' local_path must be absolute")

    # Check network configuration
    if config.network:
        if config.network.hosts:
            for host_name, host_config in config.network.hosts.items():
                if not isinstance(host_config, dict):
                    issues.append(f"Host '{host_name}' configuration must be a dictionary")

    return issues


def create_default_config(deployment_name: str, beamline: str | None = None) -> DeploymentConfig:
    """
    Create a default deployment configuration.

    Args:
        deployment_name: Name of the deployment
        beamline: Optional beamline identifier

    Returns:
        Default DeploymentConfig
    """
    metadata = DeploymentMetadata(
        name=deployment_name,
        description=f"Default configuration for {deployment_name}",
        beamline=beamline,
        created=datetime.now()
    )

    # Default sources
    sources = {
        "iocs": SourceConfig(
            repository="https://github.com/example/iocs",
            branch="main",
            type="iocs"
        ),
        "bits_deployment": SourceConfig(
            repository="https://github.com/example/bits-deployment",
            branch="main",
            type="bits"
        )
    }

    # Default analysis settings
    analysis = AnalysisSettings(
        auto_update=False,
        cache_results=True,
        generate_reports=True
    )

    return DeploymentConfig(
        deployment=metadata,
        sources=sources,
        analysis=analysis
    )


def save_deployment_config(config: DeploymentConfig, config_path: str | Path) -> None:
    """
    Save deployment configuration to file.

    Args:
        config: Configuration to save
        config_path: Path to save configuration
    """
    config_path = Path(config_path)

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict for JSON serialization
    config_dict = config.model_dump()

    # Convert datetime objects to ISO format
    if 'deployment' in config_dict:
        if 'created' in config_dict['deployment'] and config_dict['deployment']['created']:
            config_dict['deployment']['created'] = config_dict['deployment']['created'].isoformat()
        if 'updated' in config_dict['deployment'] and config_dict['deployment']['updated']:
            config_dict['deployment']['updated'] = config_dict['deployment']['updated'].isoformat()

    # Save configuration
    with open(config_path, 'w') as f:
        json.dump(config_dict, f, indent=2)

    logger.info(f"Configuration saved to {config_path}")


def list_deployments(base_path: Path | None = None) -> list[str]:
    """
    List available deployments.

    Args:
        base_path: Base path to search (defaults to bait_deployments)

    Returns:
        List of deployment names
    """
    if base_path is None:
        base_path = Path("bait_deployments")

    deployments = []

    if not base_path.exists():
        return deployments

    for item in base_path.iterdir():
        if item.is_dir() and (item / "config.json").exists():
            deployments.append(item.name)

    return sorted(deployments)


def get_deployment_path(deployment_name: str, base_path: Path | None = None) -> Path | None:
    """
    Get the path to a deployment directory.

    Args:
        deployment_name: Name of the deployment
        base_path: Base path to search (defaults to bait_deployments)

    Returns:
        Path to deployment directory if found, None otherwise
    """
    if base_path is None:
        base_path = Path("bait_deployments")

    deployment_path = base_path / deployment_name

    if deployment_path.exists() and deployment_path.is_dir():
        return deployment_path

    return None
