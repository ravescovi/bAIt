"""
Tutorial Test Agent for BITS Framework

Automated testing agent that validates BITS tutorial steps, manages containers,
detects issues, applies fixes, and provides comprehensive reporting.
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ..framework.base_agent import BaseAgent, AgentResult, AgentStatus


@dataclass
class TutorialStep:
    """Represents a single tutorial step"""
    step_number: int
    title: str
    commands: List[str]
    expected_outcomes: List[str]
    validation_criteria: List[str]
    prerequisites: List[str] = field(default_factory=list)
    timeout: int = 300  # seconds


@dataclass
class TestRun:
    """Represents a complete tutorial test run"""
    run_id: str
    start_time: float
    environment: Dict[str, Any]
    tutorial_version: str
    steps_executed: List[TutorialStep] = field(default_factory=list)
    steps_passed: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0
    total_execution_time: float = 0
    issues_detected: List[Dict[str, Any]] = field(default_factory=list)
    fixes_applied: List[Dict[str, Any]] = field(default_factory=list)


class TutorialTestAgent(BaseAgent):
    """
    Main orchestrator for BITS tutorial testing.
    
    Responsibilities:
    - Parse tutorial markdown files
    - Manage test environment and containers
    - Execute tutorial steps with monitoring
    - Detect issues and apply automatic fixes
    - Generate comprehensive test reports
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("TutorialTestAgent", config)
        
        # Core components - will be initialized in _initialize_components
        self.parser = None
        self.container_manager = None
        self.fixer = None
        self.retry_orchestrator = None
        self.rewriter = None
        
        # Configuration
        self.tutorial_path = Path(self.config.get(
            "tutorial_path", 
            "bits_base/BITS/src/bits_demo/tutorial"
        ))
        self.max_retries = self.config.get("max_retries", 3)
        self.container_timeout = self.config.get("container_timeout", 60)
        self.step_timeout = self.config.get("step_timeout", 300)
        
        # State tracking
        self.current_run: Optional[TestRun] = None
        self.tutorial_steps: List[TutorialStep] = []
        
    async def execute(
        self, 
        tutorial_files: Optional[List[str]] = None,
        clean_environment: bool = True,
        stop_on_failure: bool = False
    ) -> AgentResult:
        """
        Execute complete tutorial testing workflow.
        
        Args:
            tutorial_files: Specific tutorial files to test (default: all)
            clean_environment: Whether to start with clean environment
            stop_on_failure: Stop testing on first failure
            
        Returns:
            AgentResult with comprehensive test results
        """
        self._set_status(AgentStatus.RUNNING)
        start_time = time.time()
        
        try:
            # Initialize components
            await self._initialize_components()
            
            # Create new test run
            self.current_run = TestRun(
                run_id=f"run-{int(start_time)}",
                start_time=start_time,
                environment=await self._get_environment_info(),
                tutorial_version=await self._get_tutorial_version()
            )
            
            self.logger.info(f"Starting tutorial test run: {self.current_run.run_id}")
            
            # Parse tutorial files
            tutorial_files = tutorial_files or self._get_default_tutorial_files()
            self.tutorial_steps = await self._parse_tutorial_files(tutorial_files)
            
            self.logger.info(f"Parsed {len(self.tutorial_steps)} tutorial steps")
            
            # Setup clean environment if requested
            if clean_environment:
                await self._setup_clean_environment()
                
            # Execute tutorial steps
            for step in self.tutorial_steps:
                result = await self._execute_tutorial_step(step)
                
                if result.success:
                    self.current_run.steps_passed += 1
                    self.logger.info(f"✅ Step {step.step_number}: {step.title}")
                else:
                    self.current_run.steps_failed += 1
                    self.logger.error(f"❌ Step {step.step_number}: {step.title}")
                    
                    if stop_on_failure:
                        self.logger.info("Stopping test run due to failure")
                        break
                        
                self.current_run.steps_executed.append(step)
                
            # Calculate final metrics
            self.current_run.total_execution_time = time.time() - start_time
            
            # Generate comprehensive report
            report = await self._generate_test_report()
            
            success = self.current_run.steps_failed == 0
            message = f"Tutorial test completed: {self.current_run.steps_passed}/{len(self.current_run.steps_executed)} steps passed"
            
            result = self._create_result(
                success=success,
                message=message,
                data={
                    "test_run": self.current_run,
                    "report": report,
                    "success_rate": self.current_run.steps_passed / len(self.current_run.steps_executed) if self.current_run.steps_executed else 0
                },
                execution_time=time.time() - start_time
            )
            
            self._set_status(AgentStatus.COMPLETED)
            self._add_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tutorial test execution failed: {e}")
            self._set_status(AgentStatus.FAILED)
            
            result = self._create_result(
                success=False,
                message=f"Tutorial test execution failed: {e}",
                errors=[str(e)],
                execution_time=time.time() - start_time
            )
            
            self._add_result(result)
            return result
    
    async def _initialize_components(self):
        """Initialize all required components"""
        # Import here to avoid circular dependencies
        from .tutorial_parser import TutorialParser
        from .container_manager import ContainerManager
        from .tutorial_fixer import TutorialFixAgent
        from .retry_orchestrator import RetryOrchestrator
        from .tutorial_rewriter import TutorialRewriter
        
        self.parser = TutorialParser(self.config.get("parser_config", {}))
        self.container_manager = ContainerManager(
            self.config.get("container_config", {}),
            prefer_podman=True
        )
        self.fixer = TutorialFixAgent(self.config.get("fixer_config", {}))
        self.retry_orchestrator = RetryOrchestrator(
            self.config.get("retry_config", {}),
            container_manager=self.container_manager,
            fixer=self.fixer
        )
        self.rewriter = TutorialRewriter(self.config.get("rewriter_config", {}))
        
        self.logger.debug("Tutorial test agent components initialized")
    
    async def _get_environment_info(self) -> Dict[str, Any]:
        """Gather current environment information"""
        import platform
        import sys
        
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0]
        }
    
    async def _get_tutorial_version(self) -> str:
        """Get current tutorial version from git or config"""
        try:
            # Try to get git commit hash
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, cwd=self.tutorial_path.parent
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
        return "unknown"
    
    def _get_default_tutorial_files(self) -> List[str]:
        """Get default list of tutorial files to test"""
        return [
            "00_introduction.md",
            "01_ioc_exploration.md", 
            "02_bits_starter_setup.md",
            "03_device_configuration.md",
            "04_plan_development.md",
            "05_ipython_execution.md"
        ]
    
    async def _parse_tutorial_files(self, tutorial_files: List[str]) -> List[TutorialStep]:
        """Parse tutorial markdown files to extract executable steps"""
        steps = []
        
        for i, filename in enumerate(tutorial_files):
            file_path = self.tutorial_path / filename
            if file_path.exists():
                self.logger.debug(f"Parsing tutorial file: {filename}")
                file_steps = await self.parser.parse_file(file_path, base_step_number=i*10)
                steps.extend(file_steps)
            else:
                self.logger.warning(f"Tutorial file not found: {filename}")
                
        return steps
    
    async def _setup_clean_environment(self):
        """Setup clean testing environment"""
        self.logger.info("Setting up clean testing environment...")
        
        # Stop any existing containers
        await self.container_manager.cleanup_containers()
        
        # Setup fresh environment
        await self.container_manager.setup_tutorial_environment()
        
        self.logger.info("Clean environment ready")
    
    async def _execute_tutorial_step(self, step: TutorialStep) -> AgentResult:
        """Execute a single tutorial step with retry logic"""
        self.logger.debug(f"Executing step {step.step_number}: {step.title}")
        
        # Use retry orchestrator for robust execution
        result = await self.retry_orchestrator.execute_with_retry(
            step, max_attempts=self.max_retries
        )
        
        # Track any issues or fixes
        if hasattr(result, 'issues_detected'):
            self.current_run.issues_detected.extend(result.issues_detected)
        if hasattr(result, 'fixes_applied'):
            self.current_run.fixes_applied.extend(result.fixes_applied)
            
        return result
    
    async def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.current_run:
            return {}
            
        total_steps = len(self.current_run.steps_executed)
        success_rate = (self.current_run.steps_passed / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "summary": {
                "total_steps": total_steps,
                "passed": self.current_run.steps_passed,
                "failed": self.current_run.steps_failed,
                "skipped": self.current_run.steps_skipped,
                "success_rate": f"{success_rate:.1f}%"
            },
            "execution_metrics": {
                "total_time": f"{self.current_run.total_execution_time:.1f}s",
                "average_time_per_step": f"{self.current_run.total_execution_time / total_steps:.1f}s" if total_steps > 0 else "0s"
            },
            "issues_summary": {
                "total_issues": len(self.current_run.issues_detected),
                "critical_issues": len([i for i in self.current_run.issues_detected if i.get('severity') == 'critical']),
                "fixes_applied": len(self.current_run.fixes_applied)
            },
            "environment": self.current_run.environment,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not self.current_run:
            return recommendations
            
        # Analyze failure patterns
        if self.current_run.steps_failed > 0:
            recommendations.append("Review failed steps and update tutorial documentation")
            
        # Check for container issues
        container_issues = [i for i in self.current_run.issues_detected if 'container' in i.get('category', '')]
        if container_issues:
            recommendations.append("Update container startup timeout and error handling")
            
        # Check for environment issues
        env_issues = [i for i in self.current_run.issues_detected if 'environment' in i.get('category', '')]
        if env_issues:
            recommendations.append("Improve environment setup validation and error messages")
            
        return recommendations
    
    async def generate_tutorial_improvements(
        self,
        tutorial_files: Optional[List[str]] = None,
        apply_high_confidence: bool = False
    ) -> Dict[str, Any]:
        """
        Generate intelligent suggestions for improving tutorial content based on execution results.
        
        Args:
            tutorial_files: Specific tutorial files to analyze (default: last executed files)
            apply_high_confidence: Whether to automatically apply high-confidence suggestions
            
        Returns:
            Dictionary containing improvement suggestions and application results
        """
        if not self.rewriter:
            await self._initialize_components()
        
        results = {
            "tutorials_analyzed": [],
            "total_suggestions": 0,
            "high_confidence_suggestions": 0,
            "applied_automatically": 0,
            "improvement_reports": {},
            "summary": {}
        }
        
        if not tutorial_files and self.current_run:
            # Use files from last execution
            tutorial_files = [step.title.split(':')[0] for step in self.current_run.steps_executed]
            tutorial_files = list(set(tutorial_files))  # Remove duplicates
        
        if not tutorial_files:
            tutorial_files = ["00_introduction.md"]  # Default fallback
        
        for tutorial_file in tutorial_files:
            tutorial_path = self.tutorial_path / tutorial_file
            
            if not tutorial_path.exists():
                self.logger.warning(f"Tutorial file not found: {tutorial_path}")
                continue
            
            self.logger.info(f"🔍 Analyzing tutorial: {tutorial_file}")
            
            # Collect execution data for this tutorial
            execution_results = []
            issues_detected = []
            fixes_applied = []
            
            if self.current_run:
                # Filter results for this tutorial
                for i, step in enumerate(self.current_run.steps_executed):
                    if tutorial_file in step.title or i < len(self.current_run.steps_executed):
                        execution_results.append({
                            "step_number": step.step_number,
                            "title": step.title,
                            "commands": step.commands,
                            "success": i < self.current_run.steps_passed,
                            "error_message": getattr(step, 'error_message', None)
                        })
                
                # Convert issues and fixes to proper format
                for issue_data in self.current_run.issues_detected:
                    issues_detected.append(issue_data)
                
                fixes_applied = self.current_run.fixes_applied
            
            # Generate suggestions using the rewriter
            suggestions = await self.rewriter.analyze_tutorial_execution(
                tutorial_path,
                execution_results,
                issues_detected,
                fixes_applied
            )
            
            if not suggestions:
                self.logger.info(f"No improvements suggested for {tutorial_file}")
                continue
            
            # Generate improvement report
            improvement_report = await self.rewriter.generate_improvement_report(
                tutorial_path,
                suggestions,
                execution_results
            )
            
            results["improvement_reports"][tutorial_file] = improvement_report
            results["tutorials_analyzed"].append(tutorial_file)
            results["total_suggestions"] += len(suggestions)
            
            high_confidence = [s for s in suggestions if s.confidence > 0.8]
            results["high_confidence_suggestions"] += len(high_confidence)
            
            # Apply suggestions if requested
            if apply_high_confidence:
                application_results = await self.rewriter.apply_suggestions(
                    tutorial_path,
                    suggestions,
                    auto_apply_threshold=0.8
                )
                
                results["applied_automatically"] += application_results["total_changes"]
                
                self.logger.info(
                    f"✅ Applied {application_results['total_changes']} improvements to {tutorial_file}"
                )
                
                # Log what was applied
                for applied in application_results["applied_automatically"]:
                    self.logger.info(f"  - {applied['type']}: {applied['reason']}")
        
        # Generate summary
        results["summary"] = {
            "analysis_complete": True,
            "tutorials_processed": len(results["tutorials_analyzed"]),
            "average_suggestions_per_tutorial": (
                results["total_suggestions"] / len(results["tutorials_analyzed"])
                if results["tutorials_analyzed"] else 0
            ),
            "improvement_potential": "High" if results["high_confidence_suggestions"] > 5 else
                                   "Medium" if results["high_confidence_suggestions"] > 2 else "Low"
        }
        
        self.logger.info(
            f"🎯 Tutorial analysis complete: {results['total_suggestions']} suggestions generated, "
            f"{results['high_confidence_suggestions']} high-confidence, "
            f"{results['applied_automatically']} applied automatically"
        )
        
        return results