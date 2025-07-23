"""
Tutorial Fix Agent for BITS Framework

Automatically detects and fixes common tutorial execution issues.
"""

import asyncio
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    MAJOR = "major" 
    MINOR = "minor"
    INFO = "info"


class IssueCategory(Enum):
    """Issue categories"""
    ENVIRONMENT = "environment"
    CONTAINER = "container"
    DEPENDENCY = "dependency"
    PERMISSION = "permission"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    SYNTAX = "syntax"


@dataclass
class Issue:
    """Represents a detected issue"""
    id: str
    title: str
    description: str
    category: IssueCategory
    severity: IssueSeverity
    command: str
    error_message: str
    auto_fixable: bool = False
    fix_confidence: float = 0.0  # 0.0 to 1.0


@dataclass 
class Fix:
    """Represents an automatic fix"""
    issue_id: str
    description: str
    commands: List[str]
    validation_command: Optional[str] = None
    rollback_commands: Optional[List[str]] = None
    success: bool = False
    error_message: Optional[str] = None


class TutorialFixAgent:
    """
    Automatically fixes common tutorial issues.
    
    Features:
    - Pattern-based issue detection
    - Automatic fix generation and application
    - Rollback capability for failed fixes
    - Learning from fix success/failure
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("bait.agents.tutorial_fixer")
        
        # Fix patterns database
        self.fix_patterns = self._load_fix_patterns()
        
        # Track fix success rates
        self.fix_stats: Dict[str, Dict[str, Any]] = {}
    
    def _load_fix_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load fix patterns for common issues"""
        return {
            # Environment Issues
            "conda_env_missing": {
                "pattern": r"conda.*activate.*environment.*not.*exist",
                "category": IssueCategory.ENVIRONMENT,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.95,
                "fix_commands": [
                    "conda create -n BITS_demo python=3.11 -y",
                    "conda activate BITS_demo"
                ],
                "validation": "conda info --envs | grep BITS_demo"
            },
            
            "conda_not_found": {
                "pattern": r"conda.*command not found",
                "category": IssueCategory.DEPENDENCY,
                "severity": IssueSeverity.CRITICAL,
                "auto_fixable": False,  # Requires manual conda installation
                "fix_confidence": 0.0,
                "suggestion": "Install Anaconda or Miniconda from https://conda.io/"
            },
            
            "conda_not_initialized": {
                "pattern": r"Run 'conda init' before 'conda activate'",
                "category": IssueCategory.ENVIRONMENT,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.90,
                "fix_commands": [
                    "bash -c 'if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then source ~/miniconda3/etc/profile.d/conda.sh; elif [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then source ~/anaconda3/etc/profile.d/conda.sh; fi; conda activate BITS_demo'"
                ],
                "validation": "conda info --envs | grep BITS_demo"
            },
            
            "source_command_not_found": {
                "pattern": r"/bin/sh.*source.*not found",
                "category": IssueCategory.SYNTAX,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.95,
                "fix_template": "bash -c '{original_command}'",
                "description": "Use bash instead of sh for source commands"
            },
            
            "path_not_found": {
                "pattern": r"can't cd to (/path/to/bits_demo|bits_demo/)",
                "category": IssueCategory.CONFIGURATION,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.95,
                "fix_template": "cd {resolved_path}",
                "description": "Replace template paths with actual project paths"
            },
            
            "pip_package_missing": {
                "pattern": r"ModuleNotFoundError.*No module named '(\w+)'",
                "category": IssueCategory.DEPENDENCY,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.85,
                "fix_template": "pip install {package_name}",
                "validation": "python -c 'import {package_name}'"
            },
            
            # Container Issues
            "container_not_running": {
                "pattern": r"(container.*not.*running|connection.*refused.*5064|IOC.*not.*responding)",
                "category": IssueCategory.CONTAINER,
                "severity": IssueSeverity.CRITICAL,
                "auto_fixable": True,
                "fix_confidence": 0.90,
                "fix_commands": [
                    "podman run -itd --net=host --name adsim_ioc epics-podman:latest adsim",
                    "podman run -itd --net=host --name gp_ioc epics-podman:latest gp"
                ],
                "validation": "podman ps | grep -E '(adsim_ioc|gp_ioc)'"
            },
            
            "container_startup_timeout": {
                "pattern": r"container.*startup.*timeout",
                "category": IssueCategory.CONTAINER,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.80,
                "fix_commands": [
                    "podman stop adsim_ioc gp_ioc || true",
                    "podman rm adsim_ioc gp_ioc || true",
                    "sleep 5",
                    "podman run -itd --net=host --name adsim_ioc epics-podman:latest adsim",
                    "podman run -itd --net=host --name gp_ioc epics-podman:latest gp"
                ],
                "validation": "timeout 120 bash -c 'until caget adsim:cam1:Acquire_RBV; do sleep 2; done'"
            },
            
            "podman_not_found": {
                "pattern": r"podman.*command not found",
                "category": IssueCategory.DEPENDENCY,
                "severity": IssueSeverity.CRITICAL,
                "auto_fixable": True,
                "fix_confidence": 0.70,
                "fix_commands": [
                    "sudo apt update",
                    "sudo apt install -y podman"
                ],
                "validation": "podman --version"
            },
            
            # Permission Issues
            "permission_denied": {
                "pattern": r"Permission denied.*\.(sh|py)",
                "category": IssueCategory.PERMISSION,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.95,
                "fix_template": "chmod +x {script_path}",
                "validation": "test -x {script_path}"
            },
            
            # Network Issues
            "pv_connection_timeout": {
                "pattern": r"(caget.*timeout|PV.*connection.*timeout|caput.*timeout)",
                "category": IssueCategory.NETWORK,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.70,
                "fix_commands": [
                    "sleep 10",  # Wait for IOCs to fully start
                    "export EPICS_CA_ADDR_LIST=127.0.0.1",
                    "export EPICS_CA_AUTO_ADDR_LIST=NO"
                ],
                "validation": "caget adsim:cam1:Acquire_RBV"
            },
            
            # Python/Import Issues
            "python_import_error": {
                "pattern": r"ImportError.*No module named.*bluesky",
                "category": IssueCategory.DEPENDENCY,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.85,
                "fix_commands": [
                    "pip install bluesky[complete] apstools bits-base"
                ],
                "validation": "python -c 'import bluesky; print(bluesky.__version__)'"
            },
            
            "pythonpath_issue": {
                "pattern": r"ModuleNotFoundError.*bits",
                "category": IssueCategory.CONFIGURATION,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.80,
                "fix_commands": [
                    "cd bits_base/BITS && pip install -e ."
                ],
                "validation": "python -c 'import bits_base.BITS'"
            },
            
            # File/Path Issues
            "file_not_found": {
                "pattern": r"No such file or directory.*\.(sh|py|yml|yaml)",
                "category": IssueCategory.CONFIGURATION,
                "severity": IssueSeverity.MAJOR,
                "auto_fixable": True,
                "fix_confidence": 0.60,
                "fix_description": "Attempt to locate and update file paths"
            }
        }
    
    async def detect_issues(self, command: str, error_output: str, return_code: int) -> List[Issue]:
        """
        Detect issues from command execution results.
        
        Args:
            command: The command that was executed
            error_output: Error output from command
            return_code: Command return code
            
        Returns:
            List of detected issues
        """
        issues = []
        
        if return_code == 0:
            return issues  # No issues if command succeeded
            
        # Check each pattern against error output
        for issue_type, pattern_config in self.fix_patterns.items():
            if self._match_pattern(pattern_config["pattern"], error_output):
                issue = Issue(
                    id=f"{issue_type}_{int(time.time())}",
                    title=issue_type.replace("_", " ").title(),
                    description=pattern_config.get("description", f"Detected {issue_type}"),
                    category=pattern_config["category"],
                    severity=pattern_config["severity"],
                    command=command,
                    error_message=error_output,
                    auto_fixable=pattern_config["auto_fixable"],
                    fix_confidence=pattern_config["fix_confidence"]
                )
                issues.append(issue)
                
                self.logger.debug(f"Detected issue: {issue.title} (confidence: {issue.fix_confidence})")
                
        return issues
    
    async def generate_fixes(self, issues: List[Issue]) -> List[Fix]:
        """
        Generate automatic fixes for detected issues.
        
        Args:
            issues: List of detected issues
            
        Returns:
            List of Fix objects
        """
        fixes = []
        
        for issue in issues:
            if issue.auto_fixable and issue.fix_confidence > 0.5:
                fix = await self._generate_fix_for_issue(issue)
                if fix:
                    fixes.append(fix)
                    
        return fixes
    
    async def apply_fix(self, fix: Fix) -> bool:
        """
        Apply a specific fix.
        
        Args:
            fix: Fix to apply
            
        Returns:
            True if fix was successful
        """
        self.logger.info(f"Applying fix: {fix.description}")
        
        try:
            # Execute fix commands
            for command in fix.commands:
                self.logger.debug(f"Executing fix command: {command}")
                
                result = await self._run_command(command)
                
                if result.returncode != 0:
                    fix.success = False
                    fix.error_message = result.stderr
                    self.logger.error(f"Fix command failed: {command} - {result.stderr}")
                    return False
                    
            # Validate fix if validation command provided
            if fix.validation_command:
                self.logger.debug(f"Validating fix: {fix.validation_command}")
                
                result = await self._run_command(fix.validation_command)
                
                if result.returncode != 0:
                    fix.success = False
                    fix.error_message = f"Fix validation failed: {result.stderr}"
                    self.logger.error(f"Fix validation failed: {result.stderr}")
                    return False
                    
            fix.success = True
            self.logger.info(f"✅ Fix applied successfully: {fix.description}")
            
            # Update fix statistics
            self._update_fix_stats(fix.issue_id, True)
            
            return True
            
        except Exception as e:
            fix.success = False
            fix.error_message = str(e)
            self.logger.error(f"Error applying fix: {e}")
            
            # Update fix statistics
            self._update_fix_stats(fix.issue_id, False)
            
            return False
    
    async def rollback_fix(self, fix: Fix) -> bool:
        """
        Rollback a failed fix.
        
        Args:
            fix: Fix to rollback
            
        Returns:
            True if rollback was successful
        """
        if not fix.rollback_commands:
            self.logger.warning(f"No rollback commands available for fix: {fix.description}")
            return False
            
        self.logger.info(f"Rolling back fix: {fix.description}")
        
        try:
            for command in fix.rollback_commands:
                self.logger.debug(f"Executing rollback command: {command}")
                
                result = await self._run_command(command)
                
                if result.returncode != 0:
                    self.logger.error(f"Rollback command failed: {command} - {result.stderr}")
                    return False
                    
            self.logger.info(f"✅ Fix rolled back successfully: {fix.description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back fix: {e}")
            return False
    
    async def _generate_fix_for_issue(self, issue: Issue) -> Optional[Fix]:
        """Generate a fix for a specific issue"""
        pattern_config = self.fix_patterns.get(issue.title.lower().replace(" ", "_"))
        
        if not pattern_config:
            return None
            
        fix_commands = []
        validation_command = None
        rollback_commands = None
        
        # Handle template-based fixes
        if "fix_template" in pattern_config:
            template = pattern_config["fix_template"]
            
            # Extract parameters from error message
            params = self._extract_fix_parameters(issue.error_message, pattern_config["pattern"], issue.command)
            
            try:
                fix_commands = [template.format(**params)]
                if "validation" in pattern_config:
                    validation_command = pattern_config["validation"].format(**params)
            except KeyError as e:
                self.logger.error(f"Missing parameter for fix template: {e}")
                return None
        
        # Handle predefined fix commands
        elif "fix_commands" in pattern_config:
            fix_commands = pattern_config["fix_commands"].copy()
            validation_command = pattern_config.get("validation")
            
        else:
            self.logger.warning(f"No fix commands defined for issue: {issue.title}")
            return None
            
        return Fix(
            issue_id=issue.id,
            description=f"Fix for {issue.title}",
            commands=fix_commands,
            validation_command=validation_command,
            rollback_commands=rollback_commands
        )
    
    def _match_pattern(self, pattern: str, text: str) -> bool:
        """Check if pattern matches text"""
        import re
        return bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))
    
    def _extract_fix_parameters(self, error_message: str, pattern: str, command: str = "") -> Dict[str, str]:
        """Extract parameters from error message using pattern"""
        import re
        
        match = re.search(pattern, error_message, re.IGNORECASE)
        params = {}
        
        # Always include the original command for shell fixes
        params["original_command"] = command
        
        if match:
            groups = match.groups()
            if groups:
                # Extract package name from import errors
                if "ModuleNotFoundError" in error_message:
                    params["package_name"] = groups[0] if groups else ""
                # Extract path from path errors
                elif "can't cd to" in error_message:
                    from pathlib import Path
                    bits_demo_path = 'bits_base/BITS/src/bits_demo'
                    params["resolved_path"] = str(Path.cwd() / bits_demo_path)
                
        # Extract script path from permission errors
        if "Permission denied" in error_message:
            path_match = re.search(r"Permission denied.*?([^\s]+\.(sh|py))", error_message)
            if path_match:
                params["script_path"] = path_match.group(1)
                
        return params
    
    async def _run_command(self, command: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Execute a command with timeout"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                command, process.returncode, stdout.decode(), stderr.decode()
            )
            
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except:
                pass
            raise
    
    def _update_fix_stats(self, issue_id: str, success: bool):
        """Update fix success statistics"""
        issue_type = issue_id.split('_')[0]  # Extract issue type from ID
        
        if issue_type not in self.fix_stats:
            self.fix_stats[issue_type] = {"attempts": 0, "successes": 0}
            
        self.fix_stats[issue_type]["attempts"] += 1
        if success:
            self.fix_stats[issue_type]["successes"] += 1
            
        # Log success rate
        success_rate = self.fix_stats[issue_type]["successes"] / self.fix_stats[issue_type]["attempts"]
        self.logger.debug(f"Fix success rate for {issue_type}: {success_rate:.2%}")
    
    def get_fix_success_rates(self) -> Dict[str, float]:
        """Get fix success rates by issue type"""
        rates = {}
        
        for issue_type, stats in self.fix_stats.items():
            if stats["attempts"] > 0:
                rates[issue_type] = stats["successes"] / stats["attempts"]
            else:
                rates[issue_type] = 0.0
                
        return rates