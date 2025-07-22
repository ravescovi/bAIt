"""
Deployment Analyzer for bAIt.

This analyzer provides comprehensive analysis of entire deployment configurations,
coordinating with other specialized analyzers and providing high-level insights.
"""

import logging
from pathlib import Path
from typing import Any

from ..config import DeploymentConfig
from .base_analyzer import AnalysisResult, BaseAnalyzer

logger = logging.getLogger(__name__)


class DeploymentAnalyzer(BaseAnalyzer):
    """
    Analyzer for complete deployment configurations.

    This analyzer serves as the main entry point for deployment analysis,
    coordinating with other specialized analyzers and providing comprehensive
    insights about the entire deployment.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the deployment analyzer."""
        super().__init__("deployment", config)
        self.specialized_analyzers = {}

    def analyze(self, target: str | Path | dict[str, Any] | DeploymentConfig) -> AnalysisResult:
        """
        Analyze a deployment configuration.

        Args:
            target: Deployment configuration (path to config.json or dict)

        Returns:
            AnalysisResult with deployment analysis
        """
        self._log_analysis_start(target)

        try:
            # Load configuration
            if isinstance(target, str | Path):
                config_path = self._resolve_path(target)
                if config_path.is_dir():
                    config_path = config_path / "config.json"
                deployment_config = self._read_json(config_path)
            elif isinstance(target, dict):
                deployment_config = target
            elif isinstance(target, DeploymentConfig):
                deployment_config = target.model_dump()
            else:
                return self._create_result(
                    status="error",
                    summary="Invalid target type for deployment analysis",
                    issues=[self._create_issue("error", f"Unsupported target type: {type(target)}")]
                )

            # Validate configuration structure
            validation_result = self._validate_config(deployment_config)
            if validation_result.has_errors():
                return validation_result

            # Perform analysis
            analysis_results = self._perform_analysis(deployment_config)

            # Combine results
            result = self._combine_results(analysis_results)

            self._log_analysis_complete(result)
            return result

        except Exception as e:
            self.logger.error(f"Error during deployment analysis: {e}")
            return self._create_result(
                status="error",
                summary=f"Analysis failed: {str(e)}",
                issues=[self._create_issue("error", f"Analysis exception: {str(e)}")]
            )

    def validate_target(self, target: str | Path | dict[str, Any] | DeploymentConfig) -> bool:
        """
        Validate that the target is a valid deployment configuration.

        Args:
            target: Target to validate

        Returns:
            True if target is valid
        """
        try:
            if isinstance(target, str | Path):
                config_path = self._resolve_path(target)
                if config_path.is_dir():
                    config_path = config_path / "config.json"

                if not config_path.exists():
                    return False

                # Try to load and validate basic structure
                config = self._read_json(config_path)
                return self._has_required_fields(config)

            elif isinstance(target, dict):
                return self._has_required_fields(target)
            elif isinstance(target, DeploymentConfig):
                return True  # Already validated by Pydantic

            return False

        except Exception:
            return False

    def get_supported_formats(self) -> list[str]:
        """Get supported configuration formats."""
        return ["json"]

    def get_description(self) -> str:
        """Get analyzer description."""
        return "Analyzes complete deployment configurations including IOCs, Bluesky, MEDM, and network topology"

    def _validate_config(self, config: dict[str, Any]) -> AnalysisResult:
        """
        Validate deployment configuration structure.

        Args:
            config: Configuration to validate

        Returns:
            AnalysisResult with validation results
        """
        issues = []

        # Check required top-level fields
        required_fields = ["deployment", "sources"]
        for field in required_fields:
            if field not in config:
                issues.append(self._create_issue(
                    "error",
                    f"Missing required field: {field}",
                    location="config.json"
                ))

        # Validate deployment section
        if "deployment" in config:
            deployment = config["deployment"]
            required_deployment_fields = ["name", "description"]
            for field in required_deployment_fields:
                if field not in deployment:
                    issues.append(self._create_issue(
                        "error",
                        f"Missing required deployment field: {field}",
                        location="config.json:deployment"
                    ))

        # Validate sources section
        if "sources" in config:
            sources = config["sources"]
            if not isinstance(sources, dict):
                issues.append(self._create_issue(
                    "error",
                    "Sources section must be a dictionary",
                    location="config.json:sources"
                ))
            else:
                # Validate each source
                for source_name, source_config in sources.items():
                    if not isinstance(source_config, dict):
                        issues.append(self._create_issue(
                            "warning",
                            f"Source '{source_name}' is not properly configured",
                            location=f"config.json:sources.{source_name}"
                        ))

        status = "error" if any(issue["severity"] == "error" for issue in issues) else "success"
        summary = f"Configuration validation {'failed' if status == 'error' else 'passed'}"

        return self._create_result(
            status=status,
            summary=summary,
            issues=issues,
            details={"validated_fields": list(config.keys())}
        )

    def _perform_analysis(self, config: dict[str, Any]) -> dict[str, AnalysisResult]:
        """
        Perform comprehensive deployment analysis.

        Args:
            config: Deployment configuration

        Returns:
            Dictionary of analysis results by component
        """
        results = {}

        # Basic configuration analysis
        results["configuration"] = self._analyze_configuration(config)

        # Source analysis
        if "sources" in config:
            results["sources"] = self._analyze_sources(config["sources"])

        # Network analysis
        if "network" in config:
            results["network"] = self._analyze_network(config["network"])

        # Analysis settings
        if "analysis" in config:
            results["analysis_settings"] = self._analyze_settings(config["analysis"])

        return results

    def _analyze_configuration(self, config: dict[str, Any]) -> AnalysisResult:
        """Analyze basic configuration structure."""
        details = {}
        issues = []
        recommendations = []

        # Extract basic info
        deployment_info = config.get("deployment", {})
        details["deployment_name"] = deployment_info.get("name", "unknown")
        details["deployment_version"] = deployment_info.get("version", "unknown")
        details["beamline"] = deployment_info.get("beamline", "unknown")

        # Check for optional but recommended fields
        recommended_fields = ["maintainer", "contact", "documentation"]
        for field in recommended_fields:
            if field not in deployment_info:
                issues.append(self._create_issue(
                    "info",
                    f"Consider adding {field} to deployment configuration",
                    location="config.json:deployment"
                ))
                recommendations.append(f"Add {field} field to deployment section")

        # Analyze configuration completeness
        source_count = len(config.get("sources", {}))
        details["source_count"] = source_count

        if source_count == 0:
            issues.append(self._create_issue(
                "warning",
                "No sources configured",
                location="config.json:sources"
            ))

        return self._create_result(
            status="success",
            summary=f"Configuration analysis complete for {details['deployment_name']}",
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_sources(self, sources: dict[str, Any]) -> AnalysisResult:
        """Analyze source configurations."""
        details = {}
        issues = []
        recommendations = []

        # Analyze each source
        for source_name, source_config in sources.items():
            if not isinstance(source_config, dict):
                continue

            source_details = {}

            # Check required fields
            required_fields = ["repository"]
            for field in required_fields:
                if field not in source_config:
                    issues.append(self._create_issue(
                        "error",
                        f"Missing required field '{field}' in source '{source_name}'",
                        location=f"config.json:sources.{source_name}"
                    ))
                else:
                    source_details[field] = source_config[field]

            # Check optional fields
            optional_fields = ["branch", "local_path", "enabled"]
            for field in optional_fields:
                if field in source_config:
                    source_details[field] = source_config[field]
                elif field == "branch":
                    recommendations.append(f"Consider specifying branch for source '{source_name}'")

            details[source_name] = source_details

        return self._create_result(
            status="success",
            summary=f"Source analysis complete ({len(sources)} sources)",
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_network(self, network: dict[str, Any]) -> AnalysisResult:
        """Analyze network configuration."""
        details = {}
        issues = []

        # Extract network info
        if "hosts" in network:
            details["host_count"] = len(network["hosts"])

        if "services" in network:
            details["service_count"] = len(network["services"])

        if "subnet" in network:
            details["subnet"] = network["subnet"]

        return self._create_result(
            status="success",
            summary="Network configuration analyzed",
            details=details,
            issues=issues
        )

    def _analyze_settings(self, settings: dict[str, Any]) -> AnalysisResult:
        """Analyze analysis settings."""
        details = {}
        recommendations = []

        # Check settings
        if settings.get("auto_update", False):
            details["auto_update"] = True
        else:
            recommendations.append("Consider enabling auto_update for production deployments")

        if settings.get("cache_results", False):
            details["cache_results"] = True
        else:
            recommendations.append("Consider enabling cache_results for better performance")

        return self._create_result(
            status="success",
            summary="Analysis settings reviewed",
            details=details,
            recommendations=recommendations
        )

    def _combine_results(self, results: dict[str, AnalysisResult]) -> AnalysisResult:
        """Combine individual analysis results into overall result."""
        all_issues = []
        all_recommendations = []
        combined_details = {}

        # Collect all issues and recommendations
        for component, result in results.items():
            all_issues.extend(result.issues)
            all_recommendations.extend(result.recommendations)
            combined_details[component] = result.details

        # Determine overall status
        has_errors = any(issue["severity"] == "error" for issue in all_issues)
        has_warnings = any(issue["severity"] == "warning" for issue in all_issues)

        if has_errors:
            status = "error"
            summary = "Deployment analysis found errors"
        elif has_warnings:
            status = "warning"
            summary = "Deployment analysis found warnings"
        else:
            status = "success"
            summary = "Deployment analysis completed successfully"

        return self._create_result(
            status=status,
            summary=summary,
            details=combined_details,
            issues=all_issues,
            recommendations=list(set(all_recommendations))  # Remove duplicates
        )

    def _has_required_fields(self, config: dict[str, Any]) -> bool:
        """Check if configuration has required fields."""
        required_fields = ["deployment", "sources"]
        return all(field in config for field in required_fields)
