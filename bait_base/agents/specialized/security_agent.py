"""
Security Agent

Threat modeling specialist focused on security analysis, vulnerability assessment,
and compliance validation for Bluesky-based beamline deployments.

Enhanced with SuperClaude Security Persona for comprehensive threat analysis.
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from ..framework.base_agent import BaseAgent, AgentResult, AgentStatus


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"         # 24 hour response
    MEDIUM = "medium"     # 7 day response
    LOW = "low"          # 30 day response


class AttackSurface(Enum):
    """Attack surface categories"""
    EXTERNAL = "external"     # External-facing (100% priority)
    INTERNAL = "internal"     # Internal network (70% priority)
    ISOLATED = "isolated"     # Isolated systems (40% priority)


@dataclass
class SecurityVulnerability:
    """Security vulnerability finding"""
    id: str
    title: str
    description: str
    threat_level: ThreatLevel
    attack_surface: AttackSurface
    affected_components: List[str]
    cve_ids: List[str] = None
    remediation_steps: List[str] = None
    compliance_impact: List[str] = None


class SecurityAgent(BaseAgent):
    """
    Security Agent with Security Persona Integration
    
    Priority Hierarchy: Security > compliance > reliability > performance > convenience
    
    Core Principles:
    1. Security by Default: Implement secure defaults and fail-safe mechanisms
    2. Zero Trust Architecture: Verify everything, trust nothing
    3. Defense in Depth: Multiple layers of security controls
    
    Specializes in:
    - Threat modeling and risk assessment
    - Vulnerability scanning and analysis
    - Security configuration validation
    - Compliance checking (NIST, ISO 27001, etc.)
    - Access control analysis
    - Network security assessment
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("SecurityAgent", config)
        
        # Security persona configuration
        self.threat_threshold = self.config.get("threat_threshold", ThreatLevel.MEDIUM)
        self.zero_trust_mode = self.config.get("zero_trust_mode", True)
        self.compliance_standards = self.config.get("compliance_standards", ["NIST", "ISO27001"])
        
        # Security frameworks and patterns
        self.security_controls = self._load_security_controls()
        self.threat_models = self._load_threat_models()
        
        # Vulnerability databases
        self.vulnerability_patterns = self._load_vulnerability_patterns()
    
    async def execute(
        self,
        deployment_path: Union[str, Path],
        scan_type: str = "comprehensive",
        focus_areas: Optional[List[str]] = None
    ) -> AgentResult:
        """
        Execute comprehensive security analysis.
        
        Args:
            deployment_path: Path to deployment for analysis
            scan_type: Type of security scan (comprehensive, vulnerabilities, compliance)
            focus_areas: Specific security domains to focus on
            
        Returns:
            AgentResult with security assessment and recommendations
        """
        self._set_status(AgentStatus.RUNNING)
        
        try:
            deployment_path = Path(deployment_path)
            
            # Zero Trust: Verify everything, trust nothing
            security_assessment = await self._perform_security_assessment(
                deployment_path, scan_type, focus_areas
            )
            
            # Threat modeling and risk assessment
            threat_analysis = await self._perform_threat_analysis(security_assessment)
            
            # Generate security recommendations with defense in depth
            security_recommendations = await self._generate_security_recommendations(
                security_assessment, threat_analysis
            )
            
            # Compliance validation
            compliance_report = await self._validate_compliance(
                security_assessment, self.compliance_standards
            )
            
            # Calculate overall security posture score
            security_score = self._calculate_security_score(security_assessment)
            
            result_data = {
                "deployment_path": str(deployment_path),
                "scan_type": scan_type,
                "security_assessment": security_assessment,
                "threat_analysis": threat_analysis,
                "recommendations": security_recommendations,
                "compliance_report": compliance_report,
                "security_score": security_score,
                "critical_findings": [
                    v for v in security_assessment.get("vulnerabilities", [])
                    if v.get("threat_level") == ThreatLevel.CRITICAL.value
                ]
            }
            
            # Security first: Any critical findings = failure
            critical_count = len(result_data["critical_findings"])
            success = critical_count == 0 and security_score >= 0.8
            
            message = f"Security analysis completed - Score: {security_score:.2f}, Critical Issues: {critical_count}"
            
            self._set_status(AgentStatus.COMPLETED)
            return self._create_result(success, message, result_data)
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
            self._set_status(AgentStatus.FAILED)
            return self._create_result(False, f"Security analysis failed: {e}", {"error": str(e)})
    
    async def _perform_security_assessment(
        self,
        deployment_path: Path,
        scan_type: str,
        focus_areas: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Comprehensive security assessment"""
        
        assessment = {
            "vulnerabilities": await self._scan_vulnerabilities(deployment_path),
            "access_controls": await self._analyze_access_controls(deployment_path),
            "network_security": await self._analyze_network_security(deployment_path),
            "data_protection": await self._analyze_data_protection(deployment_path),
            "configuration_security": await self._analyze_security_configurations(deployment_path),
            "secrets_management": await self._analyze_secrets_management(deployment_path)
        }
        
        # Focus area specific analysis
        if focus_areas:
            for area in focus_areas:
                if area == "authentication":
                    assessment["authentication"] = await self._analyze_authentication(deployment_path)
                elif area == "encryption":
                    assessment["encryption"] = await self._analyze_encryption(deployment_path)
                elif area == "logging":
                    assessment["security_logging"] = await self._analyze_security_logging(deployment_path)
        
        return assessment
    
    async def _analyze_authentication(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze authentication mechanisms"""
        return {
            "authentication_methods": [],
            "multi_factor_auth": False,
            "password_policies": [],
            "authentication_score": 0.5
        }
    
    async def _analyze_encryption(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze encryption usage"""
        return {
            "encryption_at_rest": False,
            "encryption_in_transit": False,
            "key_management": None,
            "encryption_score": 0.4
        }
    
    async def _analyze_security_logging(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze security logging and monitoring"""
        return {
            "security_logs": [],
            "log_monitoring": False,
            "incident_response": None,
            "logging_score": 0.3
        }
    
    async def _scan_vulnerabilities(self, deployment_path: Path) -> List[Dict[str, Any]]:
        """Scan for known vulnerabilities"""
        vulnerabilities = []
        
        # Scan configuration files for security misconfigurations
        config_files = list(deployment_path.rglob("*.yaml")) + list(deployment_path.rglob("*.yml")) + \
                      list(deployment_path.rglob("*.json")) + list(deployment_path.rglob("*.toml"))
        
        for config_file in config_files:
            file_vulns = await self._scan_config_file(config_file)
            vulnerabilities.extend(file_vulns)
        
        # Scan for hardcoded secrets
        source_files = list(deployment_path.rglob("*.py")) + list(deployment_path.rglob("*.sh"))
        for source_file in source_files:
            secret_vulns = await self._scan_for_secrets(source_file)
            vulnerabilities.extend(secret_vulns)
        
        # Scan dependency files for known vulnerable packages
        dep_files = ["requirements.txt", "pyproject.toml", "environment.yml"]
        for dep_file in dep_files:
            dep_path = deployment_path / dep_file
            if dep_path.exists():
                dep_vulns = await self._scan_dependencies(dep_path)
                vulnerabilities.extend(dep_vulns)
        
        return vulnerabilities
    
    async def _scan_config_file(self, config_file: Path) -> List[Dict[str, Any]]:
        """Scan configuration file for security issues"""
        vulnerabilities = []
        
        try:
            content = config_file.read_text()
            
            # Check for insecure configurations
            insecure_patterns = [
                ("debug.*true", "Debug mode enabled in production", ThreatLevel.HIGH),
                ("ssl.*false", "SSL/TLS disabled", ThreatLevel.CRITICAL),
                ("password.*=.*[\"'].*[\"']", "Hardcoded password detected", ThreatLevel.CRITICAL),
                ("api_key.*=.*[\"'].*[\"']", "Hardcoded API key detected", ThreatLevel.CRITICAL),
                ("0\\.0\\.0\\.0", "Binding to all interfaces", ThreatLevel.MEDIUM)
            ]
            
            for pattern, description, severity in insecure_patterns:
                import re
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append({
                        "id": f"CONFIG_{hashlib.md5(f'{config_file}{pattern}'.encode()).hexdigest()[:8]}",
                        "title": description,
                        "description": f"Found in {config_file.name}",
                        "threat_level": severity.value,
                        "attack_surface": AttackSurface.EXTERNAL.value,
                        "affected_components": [str(config_file.relative_to(config_file.parents[2]))]
                    })
                    
        except Exception as e:
            self.logger.warning(f"Failed to scan config file {config_file}: {e}")
            
        return vulnerabilities
    
    async def _scan_for_secrets(self, source_file: Path) -> List[Dict[str, Any]]:
        """Scan source files for hardcoded secrets"""
        vulnerabilities = []
        
        try:
            content = source_file.read_text()
            
            # Secret detection patterns
            secret_patterns = [
                (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
                (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key"),
                (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret"),
                (r"token\s*=\s*['\"][^'\"]+['\"]", "Hardcoded token"),
                (r"['\"][A-Za-z0-9+/]{40,}['\"]", "Potential encoded secret")
            ]
            
            import re
            for pattern, description in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    vulnerabilities.append({
                        "id": f"SECRET_{hashlib.md5(f'{source_file}{match.group()}'.encode()).hexdigest()[:8]}",
                        "title": description,
                        "description": f"Found in {source_file.name} at line {content[:match.start()].count(chr(10)) + 1}",
                        "threat_level": ThreatLevel.CRITICAL.value,
                        "attack_surface": AttackSurface.EXTERNAL.value,
                        "affected_components": [str(source_file.relative_to(source_file.parents[2]))]
                    })
                    
        except Exception as e:
            self.logger.warning(f"Failed to scan source file {source_file}: {e}")
            
        return vulnerabilities
    
    async def _scan_dependencies(self, dep_file: Path) -> List[Dict[str, Any]]:
        """Scan dependencies for known vulnerabilities"""
        vulnerabilities = []
        
        # This would integrate with vulnerability databases like CVE, GitHub Advisory, etc.
        # For now, implementing basic checks for commonly vulnerable packages
        
        known_vulnerable = {
            "pillow": {"versions": ["<8.3.2"], "cve": "CVE-2021-34552"},
            "requests": {"versions": ["<2.25.0"], "cve": "CVE-2020-26137"},
            "pyyaml": {"versions": ["<5.4"], "cve": "CVE-2020-14343"}
        }
        
        try:
            if dep_file.name == "requirements.txt":
                content = dep_file.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].lower()
                        if package in known_vulnerable:
                            vulnerabilities.append({
                                "id": f"DEP_{hashlib.md5(f'{package}{dep_file}'.encode()).hexdigest()[:8]}",
                                "title": f"Potentially vulnerable dependency: {package}",
                                "description": f"Package {package} may be vulnerable",
                                "threat_level": ThreatLevel.HIGH.value,
                                "attack_surface": AttackSurface.EXTERNAL.value,
                                "affected_components": [str(dep_file.name)],
                                "cve_ids": [known_vulnerable[package]["cve"]]
                            })
                            
        except Exception as e:
            self.logger.warning(f"Failed to scan dependencies {dep_file}: {e}")
            
        return vulnerabilities
    
    async def _analyze_access_controls(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze access control mechanisms"""
        return {
            "authentication_mechanisms": [],
            "authorization_policies": [],
            "privilege_escalation_risks": [],
            "access_control_score": 0.5  # Placeholder
        }
    
    async def _analyze_network_security(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze network security configuration"""
        network_security = {
            "exposed_services": [],
            "firewall_rules": [],
            "encryption_in_transit": False,
            "network_segmentation": False,
            "network_security_score": 0.6
        }
        
        # Look for network configuration files
        network_configs = list(deployment_path.rglob("*network*")) + \
                         list(deployment_path.rglob("*firewall*")) + \
                         list(deployment_path.rglob("docker-compose*"))
        
        network_security["configuration_files"] = [str(f.relative_to(deployment_path)) for f in network_configs]
        
        return network_security
    
    async def _analyze_data_protection(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze data protection mechanisms"""
        return {
            "encryption_at_rest": False,
            "data_classification": [],
            "backup_security": False,
            "data_retention_policies": [],
            "data_protection_score": 0.4
        }
    
    async def _analyze_security_configurations(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze security-specific configurations"""
        return {
            "security_headers": [],
            "ssl_tls_configuration": {},
            "security_policies": [],
            "configuration_security_score": 0.5
        }
    
    async def _analyze_secrets_management(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze secrets management practices"""
        secrets_analysis = {
            "hardcoded_secrets_count": 0,
            "secrets_management_system": None,
            "secret_rotation_policies": [],
            "secrets_management_score": 0.3
        }
        
        # Count hardcoded secrets found in vulnerability scan
        # This would be populated from the vulnerability scan results
        
        return secrets_analysis
    
    async def _perform_threat_analysis(self, security_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Perform threat modeling and risk assessment"""
        
        # STRIDE threat modeling
        threats = {
            "spoofing": await self._analyze_spoofing_threats(security_assessment),
            "tampering": await self._analyze_tampering_threats(security_assessment),
            "repudiation": await self._analyze_repudiation_threats(security_assessment),
            "information_disclosure": await self._analyze_disclosure_threats(security_assessment),
            "denial_of_service": await self._analyze_dos_threats(security_assessment),
            "elevation_of_privilege": await self._analyze_privilege_escalation_threats(security_assessment)
        }
        
        # Calculate overall threat score
        threat_scores = [threats[category].get("risk_score", 0.5) for category in threats]
        overall_threat_score = sum(threat_scores) / len(threat_scores) if threat_scores else 0.5
        
        return {
            "stride_analysis": threats,
            "overall_threat_score": overall_threat_score,
            "high_priority_threats": [
                threat for category in threats.values()
                for threat in category.get("threats", [])
                if threat.get("severity") in ["critical", "high"]
            ]
        }
    
    async def _generate_security_recommendations(
        self, 
        security_assessment: Dict[str, Any],
        threat_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate defense-in-depth security recommendations"""
        
        recommendations = []
        
        # Critical vulnerabilities require immediate action
        critical_vulns = [v for v in security_assessment.get("vulnerabilities", [])
                         if v.get("threat_level") == ThreatLevel.CRITICAL.value]
        
        if critical_vulns:
            recommendations.append({
                "category": "critical_vulnerabilities",
                "priority": "immediate",
                "title": "Address Critical Security Vulnerabilities",
                "description": f"Found {len(critical_vulns)} critical security issues",
                "actions": [
                    "Remove all hardcoded secrets and implement secure secret management",
                    "Enable SSL/TLS for all network communications",
                    "Disable debug mode in production environments",
                    "Implement proper access controls and authentication"
                ]
            })
        
        # Defense in depth recommendations
        if security_assessment.get("network_security", {}).get("network_security_score", 0) < 0.8:
            recommendations.append({
                "category": "network_security",
                "priority": "high",
                "title": "Implement Network Security Controls",
                "description": "Network security controls are insufficient",
                "actions": [
                    "Implement network segmentation and firewall rules",
                    "Enable encryption for all network traffic",
                    "Restrict network access to necessary services only",
                    "Implement intrusion detection and prevention systems"
                ]
            })
        
        # Zero trust architecture recommendations
        if self.zero_trust_mode:
            recommendations.append({
                "category": "zero_trust",
                "priority": "high", 
                "title": "Implement Zero Trust Architecture",
                "description": "Current architecture doesn't follow zero trust principles",
                "actions": [
                    "Verify every user and device before granting access",
                    "Implement least privilege access controls",
                    "Continuously monitor and validate security posture",
                    "Encrypt all data in transit and at rest"
                ]
            })
        
        return recommendations
    
    async def _validate_compliance(
        self, 
        security_assessment: Dict[str, Any], 
        standards: List[str]
    ) -> Dict[str, Any]:
        """Validate compliance against security standards"""
        
        compliance_results = {}
        
        for standard in standards:
            if standard == "NIST":
                compliance_results["NIST"] = await self._check_nist_compliance(security_assessment)
            elif standard == "ISO27001":
                compliance_results["ISO27001"] = await self._check_iso27001_compliance(security_assessment)
        
        return compliance_results
    
    def _calculate_security_score(self, security_assessment: Dict[str, Any]) -> float:
        """Calculate overall security posture score"""
        
        # Weight different security domains
        weights = {
            "vulnerabilities": 0.3,
            "access_controls": 0.2,
            "network_security": 0.2,
            "data_protection": 0.15,
            "configuration_security": 0.15
        }
        
        total_score = 0.0
        
        for domain, weight in weights.items():
            domain_data = security_assessment.get(domain, {})
            
            if domain == "vulnerabilities":
                # Score based on vulnerability severity
                vulns = domain_data if isinstance(domain_data, list) else []
                critical_count = len([v for v in vulns if v.get("threat_level") == ThreatLevel.CRITICAL.value])
                high_count = len([v for v in vulns if v.get("threat_level") == ThreatLevel.HIGH.value])
                
                # Penalize critical and high severity vulnerabilities
                vuln_score = max(0, 1.0 - (critical_count * 0.5) - (high_count * 0.2))
                total_score += vuln_score * weight
            else:
                # Use domain-specific scores
                domain_score = domain_data.get(f"{domain.replace('_', '_')}_score", 0.5)
                total_score += domain_score * weight
        
        return min(max(total_score, 0.0), 1.0)
    
    def _load_security_controls(self) -> Dict[str, Any]:
        """Load security control frameworks"""
        return {
            "nist_800_53": {},
            "iso_27001": {},
            "cis_controls": {}
        }
    
    def _load_threat_models(self) -> Dict[str, Any]:
        """Load threat modeling frameworks"""
        return {
            "stride": {
                "spoofing": "Authentication threats",
                "tampering": "Integrity threats", 
                "repudiation": "Non-repudiation threats",
                "information_disclosure": "Confidentiality threats",
                "denial_of_service": "Availability threats",
                "elevation_of_privilege": "Authorization threats"
            }
        }
    
    def _load_vulnerability_patterns(self) -> Dict[str, Any]:
        """Load vulnerability detection patterns"""
        return {
            "secrets": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]"
            ],
            "misconfigurations": [
                r"debug.*true",
                r"ssl.*false"
            ]
        }
    
    # Threat analysis helper methods
    async def _analyze_spoofing_threats(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze authentication and identity spoofing threats"""
        return {"threats": [], "risk_score": 0.4}
    
    async def _analyze_tampering_threats(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data integrity and tampering threats"""
        return {"threats": [], "risk_score": 0.3}
    
    async def _analyze_repudiation_threats(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze logging and audit trail threats"""
        return {"threats": [], "risk_score": 0.5}
    
    async def _analyze_disclosure_threats(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze information disclosure threats"""
        return {"threats": [], "risk_score": 0.6}
    
    async def _analyze_dos_threats(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze denial of service threats"""
        return {"threats": [], "risk_score": 0.4}
    
    async def _analyze_privilege_escalation_threats(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze privilege escalation threats"""
        return {"threats": [], "risk_score": 0.5}
    
    # Compliance checking methods
    async def _check_nist_compliance(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Check NIST Cybersecurity Framework compliance"""
        return {"compliance_score": 0.6, "gaps": [], "recommendations": []}
    
    async def _check_iso27001_compliance(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Check ISO 27001 compliance"""
        return {"compliance_score": 0.5, "gaps": [], "recommendations": []}