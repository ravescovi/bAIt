"""
Deployment Expert Agent

Systems architecture specialist focused on deployment analysis, scalability assessment,
and long-term maintainability of Bluesky-based beamline instruments.

Enhanced with SuperClaude Architect Persona for comprehensive system design analysis.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml
import json

from ..framework.base_agent import BaseAgent, AgentResult, AgentStatus


class DeploymentExpert(BaseAgent):
    """
    Deployment Expert Agent with Architect Persona Integration
    
    Priority Hierarchy: Long-term maintainability > scalability > performance > short-term gains
    
    Core Principles:
    1. Systems Thinking: Analyze impacts across entire system
    2. Future-Proofing: Design decisions that accommodate growth  
    3. Dependency Management: Minimize coupling, maximize cohesion
    
    Specializes in:
    - Deployment architecture analysis
    - Scalability assessment  
    - Dependency mapping
    - Configuration validation
    - System health monitoring
    - Upgrade pathway planning
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("DeploymentExpert", config)
        
        # Architect persona configuration
        self.analysis_depth = self.config.get("analysis_depth", "comprehensive")
        self.scalability_threshold = self.config.get("scalability_threshold", 0.8)
        self.maintainability_weight = self.config.get("maintainability_weight", 0.9)
        
        # Analysis frameworks
        self.architecture_patterns = self._load_architecture_patterns()
        self.deployment_metrics = {}
    
    async def execute(
        self, 
        deployment_path: Union[str, Path],
        analysis_type: str = "comprehensive",
        focus_areas: Optional[List[str]] = None
    ) -> AgentResult:
        """
        Execute deployment analysis with architectural focus.
        
        Args:
            deployment_path: Path to deployment configuration
            analysis_type: Type of analysis (comprehensive, scalability, dependencies)
            focus_areas: Specific areas to focus on
            
        Returns:
            AgentResult with architectural analysis and recommendations
        """
        self._set_status(AgentStatus.RUNNING)
        
        try:
            deployment_path = Path(deployment_path)
            
            # Systems thinking: Analyze entire deployment ecosystem
            analysis_results = await self._analyze_deployment_architecture(
                deployment_path, analysis_type, focus_areas
            )
            
            # Generate architectural recommendations
            recommendations = await self._generate_architectural_recommendations(analysis_results)
            
            # Assess future-proofing capabilities
            future_proofing = await self._assess_future_proofing(analysis_results)
            
            # Calculate architectural health score
            health_score = self._calculate_architecture_health(analysis_results)
            
            result_data = {
                "deployment_path": str(deployment_path),
                "analysis_type": analysis_type,
                "architecture_analysis": analysis_results,
                "recommendations": recommendations,
                "future_proofing": future_proofing,
                "health_score": health_score,
                "quality_metrics": {
                    "maintainability": analysis_results.get("maintainability_score", 0),
                    "scalability": analysis_results.get("scalability_score", 0),
                    "modularity": analysis_results.get("modularity_score", 0)
                }
            }
            
            success = health_score >= 0.7  # Architect standard for acceptable architecture
            message = f"Deployment architecture analysis completed - Health Score: {health_score:.2f}"
            
            self._set_status(AgentStatus.COMPLETED)
            return self._create_result(success, message, result_data)
            
        except Exception as e:
            self.logger.error(f"Deployment analysis failed: {e}")
            self._set_status(AgentStatus.FAILED)
            return self._create_result(False, f"Analysis failed: {e}", {"error": str(e)})
    
    async def _analyze_deployment_architecture(
        self, 
        deployment_path: Path, 
        analysis_type: str,
        focus_areas: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Comprehensive architectural analysis of deployment"""
        
        analysis = {
            "deployment_structure": await self._analyze_deployment_structure(deployment_path),
            "dependency_graph": await self._analyze_dependencies(deployment_path),
            "configuration_coherence": await self._analyze_configuration_coherence(deployment_path),
            "scalability_patterns": await self._analyze_scalability_patterns(deployment_path),
            "maintainability_metrics": await self._analyze_maintainability(deployment_path)
        }
        
        # Focus-specific analysis
        if focus_areas:
            for area in focus_areas:
                if area == "performance":
                    analysis["performance_architecture"] = await self._analyze_performance_architecture(deployment_path)
                elif area == "security":
                    analysis["security_architecture"] = await self._analyze_security_architecture(deployment_path)
                elif area == "monitoring":
                    analysis["monitoring_architecture"] = await self._analyze_monitoring_setup(deployment_path)
        
        # Calculate composite scores
        analysis["maintainability_score"] = self._calculate_maintainability_score(analysis)
        analysis["scalability_score"] = self._calculate_scalability_score(analysis)
        analysis["modularity_score"] = self._calculate_modularity_score(analysis)
        
        return analysis
    
    async def _analyze_scalability_patterns(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze scalability patterns in the deployment"""
        return {
            "horizontal_scaling": False,
            "load_balancing": False,
            "caching_strategy": None,
            "scalability_patterns": []
        }
    
    async def _analyze_maintainability(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze maintainability aspects"""
        return {
            "code_complexity": 0.5,
            "documentation_coverage": 0.4,
            "test_coverage": 0.3,
            "maintainability_indicators": []
        }
    
    async def _analyze_performance_architecture(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze performance architecture"""
        return {
            "performance_patterns": [],
            "bottleneck_indicators": [],
            "optimization_opportunities": []
        }
    
    async def _analyze_security_architecture(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze security architecture"""
        return {
            "security_patterns": [],
            "access_controls": [],
            "encryption_usage": False
        }
    
    async def _analyze_monitoring_setup(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze monitoring and observability setup"""
        return {
            "monitoring_tools": [],
            "logging_configuration": [],
            "alerting_setup": False
        }
    
    async def _analyze_deployment_structure(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze deployment directory structure and organization"""
        structure = {
            "directory_organization": {},
            "file_organization": {},
            "naming_conventions": {},
            "separation_of_concerns": 0.0
        }
        
        if deployment_path.exists():
            # Analyze directory structure
            directories = [d for d in deployment_path.rglob("*") if d.is_dir()]
            structure["directory_organization"] = {
                "total_directories": len(directories),
                "depth_levels": max([len(d.relative_to(deployment_path).parts) for d in directories], default=0),
                "organization_patterns": self._identify_organization_patterns(directories)
            }
            
            # Analyze file organization
            files = [f for f in deployment_path.rglob("*") if f.is_file()]
            structure["file_organization"] = {
                "total_files": len(files),
                "file_types": self._categorize_files(files),
                "configuration_files": len([f for f in files if f.suffix in ['.yaml', '.yml', '.json', '.toml']])
            }
            
            # Assess separation of concerns
            structure["separation_of_concerns"] = self._assess_separation_of_concerns(deployment_path)
        
        return structure
    
    async def _analyze_dependencies(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze dependency relationships and coupling"""
        dependencies = {
            "internal_dependencies": {},
            "external_dependencies": {},
            "coupling_metrics": {},
            "dependency_violations": []
        }
        
        # Look for dependency files
        for dep_file in ["pyproject.toml", "requirements.txt", "environment.yml"]:
            dep_path = deployment_path / dep_file
            if dep_path.exists():
                dependencies["external_dependencies"][dep_file] = await self._parse_dependency_file(dep_path)
        
        # Analyze internal coupling
        dependencies["coupling_metrics"] = await self._calculate_coupling_metrics(deployment_path)
        
        return dependencies
    
    async def _analyze_configuration_coherence(self, deployment_path: Path) -> Dict[str, Any]:
        """Analyze configuration consistency and coherence"""
        coherence = {
            "configuration_files": [],
            "consistency_score": 0.0,
            "conflicts": [],
            "missing_configurations": []
        }
        
        # Find all configuration files
        config_files = []
        for pattern in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            config_files.extend(deployment_path.rglob(pattern))
        
        coherence["configuration_files"] = [str(f.relative_to(deployment_path)) for f in config_files]
        
        # Check for configuration consistency
        coherence["consistency_score"] = await self._assess_config_consistency(config_files)
        
        return coherence
    
    async def _generate_architectural_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate architecture-focused recommendations"""
        recommendations = []
        
        # Maintainability recommendations
        if analysis.get("maintainability_score", 0) < 0.8:
            recommendations.append({
                "category": "maintainability",
                "priority": "high",
                "title": "Improve Code Maintainability",
                "description": "Current maintainability score is below architect standards",
                "actions": [
                    "Refactor complex modules into smaller, focused components",
                    "Improve documentation and code comments",
                    "Standardize naming conventions across the deployment"
                ]
            })
        
        # Scalability recommendations  
        if analysis.get("scalability_score", 0) < self.scalability_threshold:
            recommendations.append({
                "category": "scalability", 
                "priority": "high",
                "title": "Enhance Scalability Architecture",
                "description": "System may not handle growth effectively",
                "actions": [
                    "Implement horizontal scaling patterns",
                    "Add resource monitoring and auto-scaling capabilities",
                    "Design for distributed deployment scenarios"
                ]
            })
        
        # Modularity recommendations
        if analysis.get("modularity_score", 0) < 0.7:
            recommendations.append({
                "category": "modularity",
                "priority": "medium", 
                "title": "Increase System Modularity",
                "description": "Components are too tightly coupled",
                "actions": [
                    "Extract common functionality into reusable modules",
                    "Define clear interfaces between components",
                    "Reduce inter-module dependencies"
                ]
            })
        
        return recommendations
    
    async def _assess_future_proofing(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess system's ability to accommodate future growth"""
        return {
            "extensibility": self._assess_extensibility(analysis),
            "upgrade_pathways": self._identify_upgrade_pathways(analysis),
            "technology_currency": self._assess_technology_currency(analysis),
            "architectural_debt": self._calculate_architectural_debt(analysis)
        }
    
    def _calculate_architecture_health(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall architectural health score"""
        maintainability = analysis.get("maintainability_score", 0) * 0.4
        scalability = analysis.get("scalability_score", 0) * 0.3  
        modularity = analysis.get("modularity_score", 0) * 0.3
        
        return maintainability + scalability + modularity
    
    def _load_architecture_patterns(self) -> Dict[str, Any]:
        """Load known architecture patterns for analysis"""
        return {
            "microservices": {"indicators": ["services/", "docker", "kubernetes"], "score_weight": 0.8},
            "modular_monolith": {"indicators": ["modules/", "packages/"], "score_weight": 0.6},
            "layered": {"indicators": ["layers/", "tiers/"], "score_weight": 0.5}
        }
    
    # Additional helper methods for comprehensive analysis
    def _identify_organization_patterns(self, directories: List[Path]) -> Dict[str, bool]:
        """Identify common organization patterns"""
        patterns = {}
        dir_names = [d.name.lower() for d in directories]
        
        patterns["domain_driven"] = any(name in dir_names for name in ["domain", "domains", "services"])
        patterns["layered_architecture"] = any(name in dir_names for name in ["controllers", "models", "views"])
        patterns["feature_based"] = len(set(dir_names) & {"features", "modules", "components"}) > 0
        
        return patterns
    
    def _categorize_files(self, files: List[Path]) -> Dict[str, int]:
        """Categorize files by type and purpose"""
        categories = {
            "configuration": 0,
            "source_code": 0, 
            "documentation": 0,
            "tests": 0,
            "deployment": 0
        }
        
        for file in files:
            if file.suffix in ['.yaml', '.yml', '.json', '.toml', '.ini']:
                categories["configuration"] += 1
            elif file.suffix in ['.py', '.js', '.ts', '.java', '.cpp']:
                categories["source_code"] += 1
            elif file.suffix in ['.md', '.rst', '.txt'] or 'readme' in file.name.lower():
                categories["documentation"] += 1
            elif 'test' in file.name.lower() or file.suffix == '.test':
                categories["tests"] += 1
            elif any(keyword in file.name.lower() for keyword in ['docker', 'deploy', 'k8s']):
                categories["deployment"] += 1
                
        return categories
    
    def _assess_separation_of_concerns(self, deployment_path: Path) -> float:
        """Assess how well concerns are separated in the deployment"""
        # Simplified assessment - could be enhanced with more sophisticated analysis
        directories = [d for d in deployment_path.rglob("*") if d.is_dir()]
        
        # Look for separation indicators
        separation_indicators = ["config", "src", "tests", "docs", "scripts"]
        found_indicators = sum(1 for indicator in separation_indicators 
                             if any(indicator in d.name.lower() for d in directories))
        
        return found_indicators / len(separation_indicators)
    
    async def _parse_dependency_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a dependency file to extract dependency information"""
        dependencies = {"dependencies": [], "dev_dependencies": [], "optional_dependencies": []}
        
        try:
            if file_path.suffix == '.toml':
                # Handle TOML files (pyproject.toml)
                try:
                    import tomllib
                except ImportError:
                    try:
                        import tomli as tomllib
                    except ImportError:
                        self.logger.warning(f"TOML library not available, skipping {file_path}")
                        return dependencies
                
                with open(file_path, 'rb') as f:
                    data = tomllib.load(f)
                    
                if 'project' in data and 'dependencies' in data['project']:
                    dependencies["dependencies"] = data['project']['dependencies']
                    
            elif file_path.name == 'requirements.txt':
                with open(file_path, 'r') as f:
                    dependencies["dependencies"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    
            elif file_path.suffix in ['.yml', '.yaml']:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'dependencies' in data:
                        dependencies["dependencies"] = data['dependencies']
                        
        except Exception as e:
            self.logger.warning(f"Failed to parse dependency file {file_path}: {e}")
            
        return dependencies
    
    async def _calculate_coupling_metrics(self, deployment_path: Path) -> Dict[str, float]:
        """Calculate coupling metrics for the deployment"""
        return {
            "afferent_coupling": 0.0,  # Incoming dependencies
            "efferent_coupling": 0.0,  # Outgoing dependencies
            "instability": 0.0,        # Resistance to change
            "abstractness": 0.0        # Level of abstraction
        }
    
    async def _assess_config_consistency(self, config_files: List[Path]) -> float:
        """Assess consistency across configuration files"""
        # Simplified assessment - could be enhanced with semantic analysis
        if not config_files:
            return 0.0
        
        consistency_score = 0.8  # Base score
        
        # Check for common patterns, naming conventions, etc.
        # This is a simplified implementation
        
        return consistency_score
    
    def _calculate_maintainability_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate maintainability score based on analysis"""
        structure_score = analysis["deployment_structure"]["separation_of_concerns"]
        config_score = analysis["configuration_coherence"]["consistency_score"]
        
        return (structure_score * 0.6) + (config_score * 0.4)
    
    def _calculate_scalability_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate scalability score"""
        # Simplified scoring based on architectural patterns
        patterns = analysis["deployment_structure"]["file_organization"]
        
        # Higher score for better organized, more modular deployments
        base_score = 0.5
        if patterns.get("configuration_files", 0) > 3:
            base_score += 0.2
        if patterns.get("total_files", 0) > 10:
            base_score += 0.1
            
        return min(base_score, 1.0)
    
    def _calculate_modularity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate modularity score"""
        structure = analysis["deployment_structure"]
        organization = structure.get("directory_organization", {})
        
        # Score based on directory organization and depth
        base_score = 0.4
        if organization.get("depth_levels", 0) >= 2:
            base_score += 0.3
        if organization.get("total_directories", 0) >= 3:
            base_score += 0.3
            
        return min(base_score, 1.0)
    
    def _assess_extensibility(self, analysis: Dict[str, Any]) -> float:
        """Assess how easy it is to extend the system"""
        return 0.7  # Placeholder - would analyze plugin systems, interfaces, etc.
    
    def _identify_upgrade_pathways(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential upgrade pathways"""
        return [
            "Gradual component modernization",
            "Configuration-driven upgrades",
            "Blue-green deployment strategy"
        ]
    
    def _assess_technology_currency(self, analysis: Dict[str, Any]) -> float:
        """Assess how current the technology stack is"""
        return 0.8  # Placeholder - would check dependency versions, EOL status, etc.
    
    def _calculate_architectural_debt(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical/architectural debt"""
        return {
            "debt_ratio": 0.2,  # Placeholder
            "critical_issues": [],
            "improvement_opportunities": []
        }