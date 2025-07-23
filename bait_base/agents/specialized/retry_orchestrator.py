"""
Retry Orchestrator for BITS Tutorial Testing

Manages progressive retry strategies with intelligent fixing and environment recovery.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from ..framework.base_agent import AgentResult
from .tutorial_test_agent import TutorialStep
from .container_manager import ContainerManager
from .tutorial_fixer import TutorialFixAgent, Issue, Fix


class RetryStrategy(Enum):
    """Retry strategy types"""
    LINEAR = "linear"          # Fixed intervals
    EXPONENTIAL = "exponential"  # Exponential backoff
    ADAPTIVE = "adaptive"      # Adaptive based on issue type


@dataclass
class RetryAttempt:
    """Information about a retry attempt"""
    attempt_number: int
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    issues_detected: List[Issue] = field(default_factory=list)
    fixes_applied: List[Fix] = field(default_factory=list)
    retry_reason: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of command execution with retry information"""
    success: bool
    final_attempt: RetryAttempt
    all_attempts: List[RetryAttempt]
    total_execution_time: float
    issues_detected: List[Issue] = field(default_factory=list)
    fixes_applied: List[Fix] = field(default_factory=list)
    
    
class RetryOrchestrator:
    """
    Orchestrates retry strategies with intelligent fixing.
    
    Features:
    - Progressive retry strategies (linear, exponential, adaptive)
    - Automatic issue detection and fixing
    - Environment recovery between retries
    - Learning from retry patterns
    """
    
    def __init__(
        self, 
        config: Optional[Dict[str, Any]] = None,
        container_manager: Optional[ContainerManager] = None,
        fixer: Optional[TutorialFixAgent] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger("bait.agents.retry_orchestrator")
        
        self.container_manager = container_manager
        self.fixer = fixer
        
        # Retry configuration
        self.default_max_attempts = self.config.get("max_attempts", 3)
        self.default_strategy = RetryStrategy(self.config.get("strategy", "adaptive"))
        self.base_delay = self.config.get("base_delay", 5)  # seconds
        self.max_delay = self.config.get("max_delay", 60)   # seconds
        
        # Retry patterns based on issue types
        self.retry_patterns = {
            "container": {
                "strategy": RetryStrategy.EXPONENTIAL,
                "max_attempts": 3,
                "base_delay": 10,
                "requires_reset": True
            },
            "dependency": {
                "strategy": RetryStrategy.LINEAR,
                "max_attempts": 2,
                "base_delay": 5,
                "requires_reset": False
            },
            "network": {
                "strategy": RetryStrategy.EXPONENTIAL,
                "max_attempts": 4,
                "base_delay": 5,
                "requires_reset": False
            },
            "environment": {
                "strategy": RetryStrategy.LINEAR,
                "max_attempts": 2,
                "base_delay": 3,
                "requires_reset": True
            },
            "permission": {
                "strategy": RetryStrategy.LINEAR,
                "max_attempts": 2,
                "base_delay": 2,
                "requires_reset": False
            }
        }
    
    def modify_command_for_retry(self, command: str, attempt: int, error: str) -> str:
        """Modify command based on retry attempt and error pattern"""
        # Conda activation fixes
        if "conda activate" in command and "Run 'conda init'" in error:
            if attempt == 2:
                return f"bash -c 'source ~/miniconda3/etc/profile.d/conda.sh && {command}'"
            elif attempt == 3:
                return f"bash -c 'source ~/anaconda3/etc/profile.d/conda.sh && {command}'"
        
        # Shell compatibility fixes
        if "source" in command and "/bin/sh" in error and "not found" in error:
            return f"bash -c '{command}'"
        
        # Path resolution fixes
        if "can't cd to" in error and "/path/to/bits_demo" in command:
            from pathlib import Path
            bits_demo_path = self.config.get('bits_demo_path', 'bits_base/BITS/src/bits_demo')
            resolved_path = str(Path.cwd() / bits_demo_path)
            return command.replace("/path/to/bits_demo", resolved_path)
        
        if "can't cd to" in error and "bits_demo/" in command:
            from pathlib import Path
            bits_demo_path = self.config.get('bits_demo_path', 'bits_base/BITS/src/bits_demo')
            resolved_path = str(Path.cwd() / bits_demo_path) + "/"
            return command.replace("bits_demo/", resolved_path)
        
        # Container image fixes
        if "manifest unknown" in error and "ghcr.io/bcda-aps/epics-podman" in command:
            return command.replace("ghcr.io/bcda-aps/epics-podman:latest", "epics-podman:latest")
        
        return command

    async def execute_with_retry(
        self, 
        step: TutorialStep, 
        max_attempts: Optional[int] = None,
        strategy: Optional[RetryStrategy] = None
    ) -> ExecutionResult:
        """
        Execute a tutorial step with intelligent retry logic.
        
        Args:
            step: Tutorial step to execute
            max_attempts: Maximum retry attempts (overrides config)
            strategy: Retry strategy (overrides config)
            
        Returns:
            ExecutionResult with comprehensive retry information
        """
        max_attempts = max_attempts or self.default_max_attempts
        strategy = strategy or self.default_strategy
        
        self.logger.info(f"Executing step {step.step_number} with retry (max {max_attempts} attempts)")
        
        start_time = time.time()
        attempts = []
        all_issues = []
        all_fixes = []
        
        for attempt_num in range(1, max_attempts + 1):
            attempt = RetryAttempt(
                attempt_number=attempt_num,
                start_time=time.time()
            )
            
            self.logger.debug(f"Attempt {attempt_num}/{max_attempts} for step {step.step_number}")
            
            # Execute step
            success, error_message = await self._execute_step(step)
            
            attempt.end_time = time.time()
            attempt.success = success
            attempt.error_message = error_message
            
            if success:
                self.logger.info(f"✅ Step {step.step_number} succeeded on attempt {attempt_num}")
                attempts.append(attempt)
                
                return ExecutionResult(
                    success=True,
                    final_attempt=attempt,
                    all_attempts=attempts,
                    total_execution_time=time.time() - start_time,
                    issues_detected=all_issues,
                    fixes_applied=all_fixes
                )
            else:
                self.logger.warning(f"❌ Step {step.step_number} failed on attempt {attempt_num}: {error_message}")
                
                # Detect issues from failure
                if self.fixer:
                    issues = await self.fixer.detect_issues(
                        command=" && ".join(step.commands),
                        error_output=error_message or "",
                        return_code=1
                    )
                    
                    attempt.issues_detected = issues
                    all_issues.extend(issues)
                    
                    # Apply fixes if this isn't the last attempt
                    if attempt_num < max_attempts:
                        fixes_applied = await self._apply_fixes_for_issues(issues)
                        attempt.fixes_applied = fixes_applied
                        all_fixes.extend(fixes_applied)
                        
                        # Check if environment reset is needed
                        if await self._should_reset_environment(issues):
                            await self._reset_environment()
                            attempt.retry_reason = "Environment reset due to critical issues"
                        else:
                            attempt.retry_reason = f"Applied {len(fixes_applied)} fixes, retrying"
                        
                        # Calculate delay for next attempt
                        delay = self._calculate_retry_delay(
                            attempt_num, strategy, issues
                        )
                        
                        if delay > 0:
                            self.logger.debug(f"Waiting {delay}s before retry...")
                            await asyncio.sleep(delay)
                
                attempts.append(attempt)
        
        # All attempts failed
        self.logger.error(f"❌ Step {step.step_number} failed after {max_attempts} attempts")
        
        return ExecutionResult(
            success=False,
            final_attempt=attempts[-1],
            all_attempts=attempts,
            total_execution_time=time.time() - start_time,
            issues_detected=all_issues,
            fixes_applied=all_fixes
        )
    
    async def _execute_step(self, step: TutorialStep) -> tuple[bool, Optional[str]]:
        """Execute a single tutorial step"""
        try:
            for command in step.commands:
                self.logger.debug(f"Executing command: {command}")
                
                # Handle different command types
                if self._is_python_command(command):
                    success, error = await self._execute_python_command(command)
                else:
                    success, error = await self._execute_bash_command(command)
                    
                if not success:
                    return False, error
                    
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def _is_python_command(self, command: str) -> bool:
        """Check if command is Python code"""
        python_indicators = [
            'import ', 'from ', 'def ', 'class ', 'print(', 'if __name__'
        ]
        
        # Don't treat bash commands as Python even if they contain python keywords
        bash_indicators = [
            'conda ', 'cd ', 'ls ', 'mkdir ', 'rm ', 'cp ', 'source ',
            'python -c ', 'python3 -c ', 'pip ', 'podman ', 'bash ', 'sh ',
            'echo ', 'grep ', 'find ', 'chmod ', 'export ', '&&', '||', '&& '
        ]
        
        if any(bash_indicator in command for bash_indicator in bash_indicators):
            return False
            
        return any(indicator in command for indicator in python_indicators)
    
    async def _execute_python_command(self, command: str) -> tuple[bool, Optional[str]]:
        """Execute Python command"""
        try:
            # Create a temporary Python file and execute it
            import tempfile
            import subprocess
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(command)
                f.flush()
                
                process = await asyncio.create_subprocess_exec(
                    'python', f.name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                # Clean up temp file
                import os
                os.unlink(f.name)
                
                if process.returncode == 0:
                    return True, None
                else:
                    return False, stderr.decode()
                    
        except Exception as e:
            return False, str(e)
    
    async def _execute_bash_command(self, command: str) -> tuple[bool, Optional[str]]:
        """Execute bash command with environment persistence"""
        try:
            # Enhance command with conda initialization if conda-related
            enhanced_command = self._enhance_command_with_environment(command)
            
            process = await asyncio.create_subprocess_shell(
                enhanced_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True,
                executable='/bin/bash'  # Force bash instead of sh
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True, None
            else:
                return False, stderr.decode()
                
        except Exception as e:
            return False, str(e)
    
    def _enhance_command_with_environment(self, command: str) -> str:
        """Enhance command with proper environment setup"""
        # If conda activate is in command, ensure conda is initialized
        if "conda activate" in command:
            conda_init = """
            if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
                source ~/miniconda3/etc/profile.d/conda.sh
            elif [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then
                source ~/anaconda3/etc/profile.d/conda.sh
            fi
            """
            return f"bash -c '{conda_init.strip()} && {command}'"
        
        # If command uses 'source', ensure it runs in bash
        if command.strip().startswith('source '):
            return f"bash -c '{command}'"
        
        return command
    
    async def _apply_fixes_for_issues(self, issues: List[Issue]) -> List[Fix]:
        """Apply fixes for detected issues"""
        if not self.fixer:
            return []
            
        fixes_applied = []
        
        # Sort issues by severity (critical first)
        sorted_issues = sorted(issues, key=lambda x: x.severity.value, reverse=True)
        
        for issue in sorted_issues:
            if issue.auto_fixable:
                self.logger.info(f"Attempting to fix: {issue.title}")
                
                fixes = await self.fixer.generate_fixes([issue])
                
                for fix in fixes:
                    success = await self.fixer.apply_fix(fix)
                    if success:
                        fixes_applied.append(fix)
                        self.logger.info(f"✅ Applied fix: {fix.description}")
                    else:
                        self.logger.error(f"❌ Failed to apply fix: {fix.description}")
                        
        return fixes_applied
    
    async def _should_reset_environment(self, issues: List[Issue]) -> bool:
        """Determine if environment reset is needed based on issues"""
        critical_categories = {'container', 'environment'}
        
        for issue in issues:
            if issue.category.value in critical_categories and issue.severity.value == 'critical':
                return True
                
        return False
    
    async def _reset_environment(self):
        """Reset the testing environment"""
        if not self.container_manager:
            return
            
        self.logger.info("Resetting environment...")
        
        try:
            # Stop and restart containers
            await self.container_manager.cleanup_containers()
            await asyncio.sleep(5)  # Give containers time to fully stop
            await self.container_manager.setup_tutorial_environment()
            
            self.logger.info("✅ Environment reset completed")
            
        except Exception as e:
            self.logger.error(f"❌ Environment reset failed: {e}")
    
    def _calculate_retry_delay(
        self, 
        attempt_number: int, 
        strategy: RetryStrategy,
        issues: List[Issue]
    ) -> float:
        """Calculate delay before next retry attempt"""
        
        # Use adaptive strategy based on issue types if available
        if issues and strategy == RetryStrategy.ADAPTIVE:
            dominant_category = self._get_dominant_issue_category(issues)
            if dominant_category in self.retry_patterns:
                pattern = self.retry_patterns[dominant_category]
                strategy = pattern["strategy"]
                base_delay = pattern["base_delay"]
            else:
                base_delay = self.base_delay
        else:
            base_delay = self.base_delay
            
        if strategy == RetryStrategy.LINEAR:
            delay = base_delay
        elif strategy == RetryStrategy.EXPONENTIAL:
            delay = base_delay * (2 ** (attempt_number - 1))
        else:  # Default to linear
            delay = base_delay
            
        # Cap at maximum delay
        return min(delay, self.max_delay)
    
    def _get_dominant_issue_category(self, issues: List[Issue]) -> str:
        """Get the dominant issue category from a list of issues"""
        if not issues:
            return "general"
            
        # Count issues by category
        category_counts = {}
        for issue in issues:
            category = issue.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
            
        # Return most common category
        return max(category_counts, key=category_counts.get)
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get statistics about retry patterns"""
        # This would be enhanced to track historical retry data
        return {
            "total_retries": 0,  # Would track actual statistics
            "success_rate": 0.0,
            "common_issues": [],
            "fix_effectiveness": {}
        }