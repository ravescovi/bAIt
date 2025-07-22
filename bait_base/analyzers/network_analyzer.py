"""
Network Analyzer for bAIt.

This analyzer provides analysis of network topology, service discovery,
and connectivity patterns for beamline deployments.
"""

import ipaddress
import logging
import socket
import subprocess
from pathlib import Path
from typing import Any

from .base_analyzer import AnalysisResult, BaseAnalyzer

logger = logging.getLogger(__name__)


class NetworkAnalyzer(BaseAnalyzer):
    """
    Analyzer for network topology and services.

    This analyzer examines network configurations, service endpoints,
    and connectivity patterns to provide insights about network setup.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Network analyzer."""
        super().__init__("network", config)

        # Common network service ports
        self.common_ports = {
            5064: "EPICS Channel Access TCP",
            5065: "EPICS Channel Access UDP",
            5075: "EPICS PVAccess TCP",
            5076: "EPICS PVAccess UDP",
            443: "HTTPS",
            80: "HTTP",
            22: "SSH",
            23: "Telnet",
            53: "DNS",
            161: "SNMP",
            162: "SNMP Trap",
            60610: "Bluesky HTTP Server",
            60615: "Bluesky Queue Server",
            8080: "HTTP Alternate",
            9090: "Prometheus",
            3000: "Grafana"
        }

        # EPICS-specific patterns
        self.epics_patterns = {
            "ca_repeater": r"ca_repeater",
            "ioc": r"ioc.*\.sh|st\.cmd",
            "procserv": r"procserv",
            "cagateway": r"cagateway",
            "archiver": r"archiver"
        }

    def analyze(self, target: str | Path | dict[str, Any]) -> AnalysisResult:
        """
        Analyze network configuration.

        Args:
            target: Network configuration (network config dict)

        Returns:
            AnalysisResult with network analysis
        """
        self._log_analysis_start(target)

        try:
            if isinstance(target, dict):
                result = self._analyze_network_config(target)
            else:
                return self._create_result(
                    status="error",
                    summary="Invalid target type for network analysis",
                    issues=[self._create_issue("error", f"Unsupported target type: {type(target)}")]
                )

            self._log_analysis_complete(result)
            return result

        except Exception as e:
            self.logger.error(f"Error during network analysis: {e}")
            return self._create_result(
                status="error",
                summary=f"Network analysis failed: {str(e)}",
                issues=[self._create_issue("error", f"Analysis exception: {str(e)}")]
            )

    def validate_target(self, target: str | Path | dict[str, Any]) -> bool:
        """
        Validate that the target is a valid network configuration.

        Args:
            target: Target to validate

        Returns:
            True if target is valid
        """
        try:
            if isinstance(target, dict):
                # Check for network configuration structure
                return any(key in target for key in ["hosts", "services", "subnet", "domain"])

            return False

        except Exception:
            return False

    def get_supported_formats(self) -> list[str]:
        """Get supported network configuration formats."""
        return ["json", "yaml"]

    def get_description(self) -> str:
        """Get analyzer description."""
        return "Analyzes network topology, service endpoints, and connectivity patterns"

    def _analyze_network_config(self, config: dict[str, Any]) -> AnalysisResult:
        """Analyze network configuration."""
        issues = []
        details = {}
        recommendations = []

        # Analyze hosts
        if "hosts" in config:
            host_analysis = self._analyze_hosts(config["hosts"])
            details["host_analysis"] = host_analysis

            # Check for issues
            if host_analysis["issues"]:
                issues.extend([
                    self._create_issue(issue["severity"], issue["message"], issue.get("location"))
                    for issue in host_analysis["issues"]
                ])

        # Analyze services
        if "services" in config:
            service_analysis = self._analyze_services(config["services"])
            details["service_analysis"] = service_analysis

            # Check for issues
            if service_analysis["issues"]:
                issues.extend([
                    self._create_issue(issue["severity"], issue["message"], issue.get("location"))
                    for issue in service_analysis["issues"]
                ])

        # Analyze network topology
        if "subnet" in config:
            topology_analysis = self._analyze_topology(config)
            details["topology_analysis"] = topology_analysis

            # Check for issues
            if topology_analysis["issues"]:
                issues.extend([
                    self._create_issue(issue["severity"], issue["message"], issue.get("location"))
                    for issue in topology_analysis["issues"]
                ])

        # Analyze connectivity
        connectivity_analysis = self._analyze_connectivity(config)
        details["connectivity_analysis"] = connectivity_analysis

        # Generate recommendations
        if details.get("host_analysis", {}).get("host_count", 0) > 10:
            recommendations.append("Large number of hosts - consider network segmentation")

        if details.get("service_analysis", {}).get("port_conflicts"):
            recommendations.append("Port conflicts detected - review service configurations")

        if not config.get("domain"):
            recommendations.append("Consider adding domain configuration for DNS resolution")

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "Network analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "Network analysis found warnings"
        else:
            status = "success"
            summary = "Network analysis completed successfully"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_hosts(self, hosts: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
        """Analyze host configurations."""
        analysis = {
            "host_count": 0,
            "host_types": {},
            "ip_addresses": [],
            "subnets": set(),
            "duplicate_ips": [],
            "invalid_ips": [],
            "issues": []
        }

        # Handle both list and dict formats
        if isinstance(hosts, list):
            host_list = hosts
        elif isinstance(hosts, dict):
            host_list = list(hosts.values())
        else:
            analysis["issues"].append({
                "severity": "error",
                "message": "Invalid hosts configuration format",
                "location": "network.hosts"
            })
            return analysis

        analysis["host_count"] = len(host_list)
        seen_ips = set()

        for host in host_list:
            if not isinstance(host, dict):
                continue

            # Analyze host type/role
            role = host.get("role", "unknown")
            if role not in analysis["host_types"]:
                analysis["host_types"][role] = 0
            analysis["host_types"][role] += 1

            # Analyze IP addresses
            ip = host.get("ip")
            if ip:
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    analysis["ip_addresses"].append(ip)

                    # Check for duplicates
                    if ip in seen_ips:
                        analysis["duplicate_ips"].append(ip)
                        analysis["issues"].append({
                            "severity": "error",
                            "message": f"Duplicate IP address: {ip}",
                            "location": f"network.hosts.{host.get('name', 'unknown')}"
                        })
                    else:
                        seen_ips.add(ip)

                    # Determine subnet
                    if ip_obj.is_private:
                        if ip_obj.version == 4:
                            # Assume /24 subnet for IPv4
                            subnet = str(ipaddress.IPv4Network(f"{ip}/24", strict=False))
                            analysis["subnets"].add(subnet)

                except ValueError:
                    analysis["invalid_ips"].append(ip)
                    analysis["issues"].append({
                        "severity": "error",
                        "message": f"Invalid IP address: {ip}",
                        "location": f"network.hosts.{host.get('name', 'unknown')}"
                    })

        # Convert set to list for JSON serialization
        analysis["subnets"] = list(analysis["subnets"])

        return analysis

    def _analyze_services(self, services: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
        """Analyze service configurations."""
        analysis = {
            "service_count": 0,
            "service_types": {},
            "ports": [],
            "port_conflicts": [],
            "epics_services": [],
            "unknown_services": [],
            "issues": []
        }

        # Handle both list and dict formats
        if isinstance(services, list):
            service_list = services
        elif isinstance(services, dict):
            service_list = list(services.values())
        else:
            analysis["issues"].append({
                "severity": "error",
                "message": "Invalid services configuration format",
                "location": "network.services"
            })
            return analysis

        analysis["service_count"] = len(service_list)
        port_usage = {}

        for service in service_list:
            if not isinstance(service, dict):
                continue

            name = service.get("name", "unknown")
            port = service.get("port")
            protocol = service.get("protocol", "tcp")

            if port:
                port_key = f"{port}/{protocol}"
                analysis["ports"].append(port_key)

                # Check for port conflicts
                if port_key in port_usage:
                    analysis["port_conflicts"].append({
                        "port": port,
                        "protocol": protocol,
                        "services": [port_usage[port_key], name]
                    })
                    analysis["issues"].append({
                        "severity": "warning",
                        "message": f"Port conflict: {port}/{protocol} used by multiple services",
                        "location": f"network.services.{name}"
                    })
                else:
                    port_usage[port_key] = name

                # Identify service type
                if port in self.common_ports:
                    service_type = self.common_ports[port]
                    if service_type not in analysis["service_types"]:
                        analysis["service_types"][service_type] = 0
                    analysis["service_types"][service_type] += 1

                    # Check for EPICS services
                    if "EPICS" in service_type:
                        analysis["epics_services"].append({
                            "name": name,
                            "port": port,
                            "type": service_type
                        })
                else:
                    analysis["unknown_services"].append({
                        "name": name,
                        "port": port,
                        "protocol": protocol
                    })

        return analysis

    def _analyze_topology(self, config: dict[str, Any]) -> dict[str, Any]:
        """Analyze network topology."""
        analysis = {
            "subnets": [],
            "network_segments": [],
            "broadcast_domains": [],
            "issues": []
        }

        # Analyze subnet configuration
        subnet = config.get("subnet")
        if subnet:
            try:
                network = ipaddress.ip_network(subnet, strict=False)
                analysis["subnets"].append({
                    "network": str(network),
                    "network_address": str(network.network_address),
                    "broadcast_address": str(network.broadcast_address),
                    "num_hosts": network.num_addresses - 2,  # Exclude network and broadcast
                    "version": network.version
                })

                # Check if hosts are in the subnet
                hosts = config.get("hosts", [])
                if isinstance(hosts, list):
                    for host in hosts:
                        if isinstance(host, dict) and "ip" in host:
                            try:
                                host_ip = ipaddress.ip_address(host["ip"])
                                if host_ip not in network:
                                    analysis["issues"].append({
                                        "severity": "warning",
                                        "message": f"Host {host.get('name', 'unknown')} IP {host['ip']} is not in subnet {subnet}",
                                        "location": f"network.hosts.{host.get('name', 'unknown')}"
                                    })
                            except ValueError:
                                pass  # Invalid IP already handled in host analysis

            except ValueError:
                analysis["issues"].append({
                    "severity": "error",
                    "message": f"Invalid subnet configuration: {subnet}",
                    "location": "network.subnet"
                })

        return analysis

    def _analyze_connectivity(self, config: dict[str, Any]) -> dict[str, Any]:
        """Analyze connectivity patterns."""
        analysis = {
            "connection_matrix": {},
            "service_dependencies": [],
            "potential_issues": [],
            "recommendations": []
        }

        # Analyze EPICS connectivity
        hosts = config.get("hosts", [])
        services = config.get("services", [])

        if isinstance(hosts, list) and isinstance(services, list):
            # Look for EPICS CA repeater
            ca_repeater_found = False
            for service in services:
                if isinstance(service, dict) and "ca_repeater" in service.get("name", "").lower():
                    ca_repeater_found = True
                    break

            if not ca_repeater_found:
                analysis["potential_issues"].append({
                    "type": "missing_service",
                    "message": "EPICS CA repeater not found in services",
                    "impact": "EPICS clients may have connectivity issues"
                })
                analysis["recommendations"].append("Consider adding EPICS CA repeater service")

            # Look for IOC hosts
            ioc_hosts = [h for h in hosts if isinstance(h, dict) and h.get("role") == "ioc_host"]
            if ioc_hosts:
                analysis["service_dependencies"].append({
                    "type": "ioc_dependency",
                    "ioc_hosts": len(ioc_hosts),
                    "message": f"Found {len(ioc_hosts)} IOC hosts that depend on EPICS services"
                })

        return analysis

    def _check_connectivity(self, host: str, port: int, timeout: int = 5) -> bool:
        """Check if a host:port is reachable (for future use)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _ping_host(self, host: str, timeout: int = 5) -> bool:
        """Ping a host to check basic connectivity (for future use)."""
        try:
            # Use ping command with timeout
            cmd = ["ping", "-c", "1", "-W", str(timeout), host]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1)
            return result.returncode == 0
        except Exception:
            return False
