"""
Query System for bAIt.

This module provides a basic natural language query system for deployment
analysis and information retrieval.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from .analyzers import (
    BlueskyAnalyzer,
    DeploymentAnalyzer,
    IOCAnalyzer,
    MEDMAnalyzer,
    NetworkAnalyzer,
)
from .config import DeploymentConfig

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a query operation."""
    query: str
    answer: str
    confidence: float
    source: str
    details: dict[str, Any]
    related_data: list[dict[str, Any]]


class QueryProcessor:
    """
    Natural language query processor for deployment analysis.

    This class provides basic natural language processing for common
    deployment queries and routes them to appropriate analyzers.
    """

    def __init__(self):
        """Initialize the query processor."""
        self.analyzers = {
            "deployment": DeploymentAnalyzer(),
            "ioc": IOCAnalyzer(),
            "bluesky": BlueskyAnalyzer(),
            "medm": MEDMAnalyzer(),
            "network": NetworkAnalyzer()
        }

        # Query patterns and their handlers
        self.query_patterns = {
            # IOC-related queries
            r"(?:what|which|how many) iocs? (?:are|is) (?:running|configured|available)": self._handle_ioc_list_query,
            r"(?:what|which) pvs? (?:are|is) (?:available|defined|configured)": self._handle_pv_list_query,
            r"(?:what|which) (?:epics )?records? (?:are|is) (?:available|defined|configured)": self._handle_record_query,
            r"(?:what|which) startup files? (?:are|is) (?:available|configured)": self._handle_startup_query,

            # Bluesky-related queries
            r"(?:what|which) devices? (?:are|is) (?:available|configured|defined)": self._handle_device_query,
            r"(?:what|which) plans? (?:are|is) (?:available|configured|defined)": self._handle_plan_query,
            r"(?:what|which) (?:bluesky )?configurations? (?:are|is) (?:available|configured)": self._handle_bluesky_config_query,

            # MEDM-related queries
            r"(?:what|which) (?:medm )?screens? (?:are|is) (?:available|configured)": self._handle_medm_screen_query,
            r"(?:what|which) (?:control )?interfaces? (?:are|is) (?:available|configured)": self._handle_interface_query,

            # Network-related queries
            r"(?:what|which) hosts? (?:are|is) (?:available|configured|running)": self._handle_host_query,
            r"(?:what|which) services? (?:are|is) (?:available|configured|running)": self._handle_service_query,
            r"(?:what|which) ports? (?:are|is) (?:open|configured|used)": self._handle_port_query,
            r"(?:what|which) (?:network )?topology": self._handle_topology_query,

            # General deployment queries
            r"(?:what|which) (?:is|are) (?:the )?(?:deployment|system|beamline) (?:status|health|configuration)": self._handle_deployment_status_query,
            r"(?:what|which) (?:components|parts) (?:are|is) (?:available|configured|running)": self._handle_component_query,
            r"(?:what|which) (?:issues|problems|warnings|errors) (?:are|is) (?:found|detected|present)": self._handle_issue_query,

            # Help queries
            r"(?:what|which) (?:can|could) (?:i|you) (?:do|ask|query)": self._handle_help_query,
            r"help|usage|commands": self._handle_help_query,
        }

        # Analysis cache
        self._analysis_cache = {}

    def query(self, deployment_config: DeploymentConfig, query_text: str) -> QueryResult:
        """
        Process a natural language query.

        Args:
            deployment_config: Deployment configuration
            query_text: Natural language query

        Returns:
            QueryResult with answer and details
        """
        try:
            # Normalize query text
            normalized_query = query_text.lower().strip()

            # Find matching pattern
            handler = self._find_query_handler(normalized_query)

            if handler:
                # Execute the handler
                result = handler(deployment_config, normalized_query)
                result.query = query_text
                return result
            else:
                # No specific handler found, try general analysis
                return self._handle_general_query(deployment_config, query_text)

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResult(
                query=query_text,
                answer=f"Sorry, I encountered an error processing your query: {str(e)}",
                confidence=0.0,
                source="error",
                details={},
                related_data=[]
            )

    def _find_query_handler(self, query_text: str) -> callable | None:
        """Find the appropriate query handler based on patterns."""
        for pattern, handler in self.query_patterns.items():
            if re.search(pattern, query_text, re.IGNORECASE):
                return handler
        return None

    def _get_deployment_analysis(self, deployment_config: DeploymentConfig) -> dict[str, Any]:
        """Get cached deployment analysis or perform new analysis."""
        cache_key = f"deployment_{deployment_config.deployment.name}"

        if cache_key not in self._analysis_cache:
            result = self.analyzers["deployment"].analyze(deployment_config)
            self._analysis_cache[cache_key] = result

        return self._analysis_cache[cache_key]

    def _handle_ioc_list_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle IOC-related queries."""
        analysis = self._get_deployment_analysis(deployment_config)

        # Extract IOC information from sources
        ioc_sources = {}
        if "sources" in analysis.details:
            for source_name, source_data in analysis.details["sources"].items():
                if "ioc" in source_name.lower():
                    ioc_sources[source_name] = source_data

        if ioc_sources:
            ioc_count = len(ioc_sources)
            ioc_names = list(ioc_sources.keys())

            answer = f"Found {ioc_count} IOC configuration(s): {', '.join(ioc_names)}"
            confidence = 0.9

            return QueryResult(
                query=query,
                answer=answer,
                confidence=confidence,
                source="deployment_analysis",
                details={"ioc_sources": ioc_sources},
                related_data=[{"type": "ioc", "name": name, "data": data} for name, data in ioc_sources.items()]
            )
        else:
            return QueryResult(
                query=query,
                answer="No IOC configurations found in this deployment.",
                confidence=0.8,
                source="deployment_analysis",
                details={},
                related_data=[]
            )

    def _handle_pv_list_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle PV-related queries."""
        # This would require analyzing IOC database files
        return QueryResult(
            query=query,
            answer="PV analysis requires IOC database file analysis, which is not yet fully implemented.",
            confidence=0.5,
            source="placeholder",
            details={},
            related_data=[]
        )

    def _handle_record_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle EPICS record queries."""
        return QueryResult(
            query=query,
            answer="EPICS record analysis requires database file parsing, which is not yet fully implemented.",
            confidence=0.5,
            source="placeholder",
            details={},
            related_data=[]
        )

    def _handle_startup_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle startup file queries."""
        return QueryResult(
            query=query,
            answer="Startup file analysis is available but requires access to the actual files.",
            confidence=0.6,
            source="placeholder",
            details={},
            related_data=[]
        )

    def _handle_device_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle Bluesky device queries."""
        # Look for Bluesky sources
        analysis = self._get_deployment_analysis(deployment_config)

        bluesky_sources = {}
        if "sources" in analysis.details:
            for source_name, source_data in analysis.details["sources"].items():
                if "bluesky" in source_name.lower() or "bits" in source_name.lower():
                    bluesky_sources[source_name] = source_data

        if bluesky_sources:
            source_count = len(bluesky_sources)
            source_names = list(bluesky_sources.keys())

            answer = f"Found {source_count} Bluesky source(s): {', '.join(source_names)}. Device analysis requires access to the actual configuration files."
            confidence = 0.7

            return QueryResult(
                query=query,
                answer=answer,
                confidence=confidence,
                source="deployment_analysis",
                details={"bluesky_sources": bluesky_sources},
                related_data=[{"type": "bluesky", "name": name, "data": data} for name, data in bluesky_sources.items()]
            )
        else:
            return QueryResult(
                query=query,
                answer="No Bluesky configurations found in this deployment.",
                confidence=0.8,
                source="deployment_analysis",
                details={},
                related_data=[]
            )

    def _handle_plan_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle Bluesky plan queries."""
        return QueryResult(
            query=query,
            answer="Bluesky plan analysis requires access to the actual Python files.",
            confidence=0.6,
            source="placeholder",
            details={},
            related_data=[]
        )

    def _handle_bluesky_config_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle Bluesky configuration queries."""
        return self._handle_device_query(deployment_config, query)

    def _handle_medm_screen_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle MEDM screen queries."""
        analysis = self._get_deployment_analysis(deployment_config)

        medm_sources = {}
        if "sources" in analysis.details:
            for source_name, source_data in analysis.details["sources"].items():
                if "medm" in source_name.lower():
                    medm_sources[source_name] = source_data

        if medm_sources:
            source_count = len(medm_sources)
            source_names = list(medm_sources.keys())

            answer = f"Found {source_count} MEDM screen source(s): {', '.join(source_names)}. Screen analysis requires access to the actual .adl files."
            confidence = 0.7

            return QueryResult(
                query=query,
                answer=answer,
                confidence=confidence,
                source="deployment_analysis",
                details={"medm_sources": medm_sources},
                related_data=[{"type": "medm", "name": name, "data": data} for name, data in medm_sources.items()]
            )
        else:
            return QueryResult(
                query=query,
                answer="No MEDM screen configurations found in this deployment.",
                confidence=0.8,
                source="deployment_analysis",
                details={},
                related_data=[]
            )

    def _handle_interface_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle control interface queries."""
        return self._handle_medm_screen_query(deployment_config, query)

    def _handle_host_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle host queries."""
        if hasattr(deployment_config, 'network') and deployment_config.network:
            network_analysis = self.analyzers["network"].analyze(deployment_config.network.model_dump())

            if "host_analysis" in network_analysis.details:
                host_analysis = network_analysis.details["host_analysis"]
                host_count = host_analysis.get("host_count", 0)
                host_types = host_analysis.get("host_types", {})

                answer = f"Found {host_count} host(s) configured"
                if host_types:
                    type_summary = ", ".join([f"{count} {role}" for role, count in host_types.items()])
                    answer += f": {type_summary}"

                return QueryResult(
                    query=query,
                    answer=answer,
                    confidence=0.9,
                    source="network_analysis",
                    details={"host_analysis": host_analysis},
                    related_data=[{"type": "host", "data": host_analysis}]
                )

        return QueryResult(
            query=query,
            answer="No network configuration found in this deployment.",
            confidence=0.8,
            source="network_analysis",
            details={},
            related_data=[]
        )

    def _handle_service_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle service queries."""
        if hasattr(deployment_config, 'network') and deployment_config.network:
            network_analysis = self.analyzers["network"].analyze(deployment_config.network.model_dump())

            if "service_analysis" in network_analysis.details:
                service_analysis = network_analysis.details["service_analysis"]
                service_count = service_analysis.get("service_count", 0)
                service_types = service_analysis.get("service_types", {})

                answer = f"Found {service_count} service(s) configured"
                if service_types:
                    type_summary = ", ".join([f"{count} {service_type}" for service_type, count in service_types.items()])
                    answer += f": {type_summary}"

                return QueryResult(
                    query=query,
                    answer=answer,
                    confidence=0.9,
                    source="network_analysis",
                    details={"service_analysis": service_analysis},
                    related_data=[{"type": "service", "data": service_analysis}]
                )

        return QueryResult(
            query=query,
            answer="No network services found in this deployment.",
            confidence=0.8,
            source="network_analysis",
            details={},
            related_data=[]
        )

    def _handle_port_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle port queries."""
        return self._handle_service_query(deployment_config, query)

    def _handle_topology_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle network topology queries."""
        if hasattr(deployment_config, 'network') and deployment_config.network:
            network_config = deployment_config.network.model_dump()

            subnet = network_config.get("subnet")
            domain = network_config.get("domain")

            answer = "Network topology: "
            if subnet:
                answer += f"Subnet: {subnet}"
            if domain:
                answer += f", Domain: {domain}"

            if not subnet and not domain:
                answer += "No specific topology information configured"

            return QueryResult(
                query=query,
                answer=answer,
                confidence=0.8,
                source="network_analysis",
                details={"network_config": network_config},
                related_data=[{"type": "topology", "data": network_config}]
            )

        return QueryResult(
            query=query,
            answer="No network topology configuration found in this deployment.",
            confidence=0.8,
            source="network_analysis",
            details={},
            related_data=[]
        )

    def _handle_deployment_status_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle deployment status queries."""
        analysis = self._get_deployment_analysis(deployment_config)

        deployment_name = deployment_config.deployment.name
        beamline = deployment_config.deployment.beamline
        source_count = len(deployment_config.sources)

        answer = f"Deployment '{deployment_name}'"
        if beamline:
            answer += f" (Beamline: {beamline})"

        answer += f" has {source_count} configured source(s)"

        if analysis.issues:
            issue_count = len(analysis.issues)
            error_count = len([i for i in analysis.issues if i.get("severity") == "error"])
            warning_count = len([i for i in analysis.issues if i.get("severity") == "warning"])

            answer += f" with {issue_count} issue(s)"
            if error_count > 0:
                answer += f" ({error_count} error(s), {warning_count} warning(s))"
        else:
            answer += " with no issues detected"

        return QueryResult(
            query=query,
            answer=answer,
            confidence=0.9,
            source="deployment_analysis",
            details={"deployment_analysis": analysis.details},
            related_data=[{"type": "deployment", "data": analysis.details}]
        )

    def _handle_component_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle component queries."""
        analysis = self._get_deployment_analysis(deployment_config)

        components = []
        if "sources" in analysis.details:
            for source_name, source_data in analysis.details["sources"].items():
                components.append(f"{source_name} ({source_data.get('repository', 'unknown')})")

        if components:
            answer = f"Found {len(components)} component(s): {', '.join(components)}"
            confidence = 0.9
        else:
            answer = "No components found in this deployment."
            confidence = 0.8

        return QueryResult(
            query=query,
            answer=answer,
            confidence=confidence,
            source="deployment_analysis",
            details={"components": components},
            related_data=[{"type": "component", "data": components}]
        )

    def _handle_issue_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle issue queries."""
        analysis = self._get_deployment_analysis(deployment_config)

        if analysis.issues:
            issue_count = len(analysis.issues)
            error_count = len([i for i in analysis.issues if i.get("severity") == "error"])
            warning_count = len([i for i in analysis.issues if i.get("severity") == "warning"])
            info_count = len([i for i in analysis.issues if i.get("severity") == "info"])

            answer = f"Found {issue_count} issue(s): {error_count} error(s), {warning_count} warning(s), {info_count} info message(s)"

            # Include first few issues
            if issue_count > 0:
                issue_list = []
                for issue in analysis.issues[:3]:  # Show first 3 issues
                    issue_list.append(f"{issue.get('severity', 'unknown').upper()}: {issue.get('message', 'unknown')}")
                answer += f". Issues: {'; '.join(issue_list)}"

                if issue_count > 3:
                    answer += f" (and {issue_count - 3} more)"

            confidence = 0.9
        else:
            answer = "No issues found in this deployment."
            confidence = 0.9

        return QueryResult(
            query=query,
            answer=answer,
            confidence=confidence,
            source="deployment_analysis",
            details={"issues": analysis.issues},
            related_data=[{"type": "issue", "data": analysis.issues}]
        )

    def _handle_help_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle help queries."""
        help_text = """
I can help you analyze deployments and answer questions about:

• IOCs: "What IOCs are running?" or "Which startup files are available?"
• Devices: "What devices are configured?" or "Which Bluesky configurations are available?"
• Screens: "What MEDM screens are available?" or "Which control interfaces are configured?"
• Network: "What hosts are configured?" or "Which services are running?"
• Status: "What is the deployment status?" or "What issues are found?"
• Components: "What components are available?"

You can ask questions in natural language, and I'll do my best to provide helpful answers based on the deployment configuration.
"""

        return QueryResult(
            query=query,
            answer=help_text.strip(),
            confidence=1.0,
            source="help_system",
            details={},
            related_data=[]
        )

    def _handle_general_query(self, deployment_config: DeploymentConfig, query: str) -> QueryResult:
        """Handle general queries that don't match specific patterns."""
        # Try to extract key terms and provide a general response
        query_lower = query.lower()

        # Check if query contains key terms
        if any(term in query_lower for term in ["ioc", "epics", "pv", "record"]):
            return QueryResult(
                query=query,
                answer="This appears to be an IOC/EPICS related query. Try asking 'What IOCs are running?' or 'What PVs are available?'",
                confidence=0.5,
                source="general_handler",
                details={},
                related_data=[]
            )
        elif any(term in query_lower for term in ["device", "bluesky", "plan", "scan"]):
            return QueryResult(
                query=query,
                answer="This appears to be a Bluesky related query. Try asking 'What devices are configured?' or 'What plans are available?'",
                confidence=0.5,
                source="general_handler",
                details={},
                related_data=[]
            )
        elif any(term in query_lower for term in ["screen", "medm", "interface", "gui"]):
            return QueryResult(
                query=query,
                answer="This appears to be a MEDM/interface related query. Try asking 'What MEDM screens are available?' or 'What control interfaces are configured?'",
                confidence=0.5,
                source="general_handler",
                details={},
                related_data=[]
            )
        elif any(term in query_lower for term in ["host", "network", "service", "port"]):
            return QueryResult(
                query=query,
                answer="This appears to be a network related query. Try asking 'What hosts are configured?' or 'What services are running?'",
                confidence=0.5,
                source="general_handler",
                details={},
                related_data=[]
            )
        else:
            return QueryResult(
                query=query,
                answer="I'm not sure how to answer that question. Try asking 'help' to see what I can help you with.",
                confidence=0.3,
                source="general_handler",
                details={},
                related_data=[]
            )

    def clear_cache(self):
        """Clear the analysis cache."""
        self._analysis_cache.clear()
