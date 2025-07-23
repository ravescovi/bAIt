"""
Tutorial Rewriter Agent for BITS Framework

Automatically suggests and applies improvements to tutorial markdown files
based on execution results and issue patterns.
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .tutorial_fixer import Issue, Fix, IssueCategory, IssueSeverity


class RewriteType(Enum):
    """Types of tutorial rewrites"""
    COMMAND_UPDATE = "command_update"
    PATH_CORRECTION = "path_correction"
    PREREQUISITE_ADD = "prerequisite_add"
    EXPLANATION_ENHANCE = "explanation_enhance"
    EXAMPLE_IMPROVE = "example_improve"
    TROUBLESHOOTING_ADD = "troubleshooting_add"


@dataclass
class TutorialSuggestion:
    """Represents a suggestion for improving tutorial content"""
    rewrite_type: RewriteType
    section: str
    line_number: int
    original_content: str
    suggested_content: str
    reason: str
    confidence: float  # 0.0 to 1.0
    issue_category: Optional[IssueCategory] = None
    automated: bool = True  # Can be applied automatically


class TutorialRewriter:
    """
    Intelligent tutorial rewriter that learns from execution failures
    and suggests improvements to make tutorials more robust.
    
    Features:
    - Automatic command correction based on execution results
    - Path resolution and correction
    - Prerequisite detection and addition
    - Troubleshooting section generation
    - Environment-specific adaptations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("bait.agents.tutorial_rewriter")
        
        # Track patterns from execution results
        self.execution_history: List[Dict[str, Any]] = []
        self.common_issues: Dict[str, int] = {}
        
    async def analyze_tutorial_execution(
        self, 
        tutorial_file: Path,
        execution_results: List[Dict[str, Any]],
        issues_detected: List[Issue],
        fixes_applied: List[Fix]
    ) -> List[TutorialSuggestion]:
        """
        Analyze tutorial execution results and generate improvement suggestions.
        
        Args:
            tutorial_file: Path to the tutorial markdown file
            execution_results: Results from each step execution
            issues_detected: Issues found during execution
            fixes_applied: Fixes that were successfully applied
            
        Returns:
            List of tutorial improvement suggestions
        """
        self.logger.info(f"Analyzing tutorial execution for: {tutorial_file}")
        
        suggestions = []
        
        # Read current tutorial content
        tutorial_content = await self._read_tutorial_file(tutorial_file)
        
        # Generate suggestions based on different analysis types
        suggestions.extend(await self._analyze_command_failures(tutorial_content, execution_results))
        suggestions.extend(await self._analyze_successful_fixes(tutorial_content, fixes_applied))
        suggestions.extend(await self._analyze_common_patterns(tutorial_content, issues_detected))
        suggestions.extend(await self._suggest_prerequisites(tutorial_content, issues_detected))
        suggestions.extend(await self._enhance_troubleshooting(tutorial_content, issues_detected))
        
        # Sort by confidence and importance
        suggestions.sort(key=lambda x: (x.confidence, x.rewrite_type.value), reverse=True)
        
        return suggestions
    
    async def apply_suggestions(
        self,
        tutorial_file: Path,
        suggestions: List[TutorialSuggestion],
        auto_apply_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Apply tutorial suggestions automatically or generate manual review.
        
        Args:
            tutorial_file: Path to tutorial file
            suggestions: List of suggestions to apply
            auto_apply_threshold: Confidence threshold for automatic application
            
        Returns:
            Results of suggestion application
        """
        results = {
            "applied_automatically": [],
            "requires_review": [],
            "backup_created": False,
            "total_changes": 0
        }
        
        if not suggestions:
            return results
        
        # Create backup of original file
        backup_path = tutorial_file.with_suffix(f"{tutorial_file.suffix}.backup")
        await self._create_backup(tutorial_file, backup_path)
        results["backup_created"] = True
        
        # Read current content
        tutorial_content = await self._read_tutorial_file(tutorial_file)
        modified_content = tutorial_content
        
        # Apply high-confidence suggestions automatically
        for suggestion in suggestions:
            if suggestion.confidence >= auto_apply_threshold and suggestion.automated:
                try:
                    modified_content = await self._apply_suggestion(modified_content, suggestion)
                    results["applied_automatically"].append({
                        "type": suggestion.rewrite_type.value,
                        "section": suggestion.section,
                        "reason": suggestion.reason,
                        "confidence": suggestion.confidence
                    })
                    results["total_changes"] += 1
                    self.logger.info(f"✅ Applied suggestion: {suggestion.reason}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to apply suggestion: {e}")
            else:
                results["requires_review"].append({
                    "type": suggestion.rewrite_type.value,
                    "section": suggestion.section,
                    "original": suggestion.original_content,
                    "suggested": suggestion.suggested_content,
                    "reason": suggestion.reason,
                    "confidence": suggestion.confidence
                })
        
        # Write modified content if changes were made
        if results["total_changes"] > 0:
            await self._write_tutorial_file(tutorial_file, modified_content)
            self.logger.info(f"✅ Applied {results['total_changes']} changes to {tutorial_file}")
        
        return results
    
    async def generate_improvement_report(
        self,
        tutorial_file: Path,
        suggestions: List[TutorialSuggestion],
        execution_results: List[Dict[str, Any]]
    ) -> str:
        """Generate a comprehensive improvement report"""
        report_lines = [
            f"# Tutorial Improvement Report: {tutorial_file.name}",
            f"Generated: {asyncio.get_event_loop().time()}",
            "",
            "## Executive Summary",
            f"- **Total Suggestions**: {len(suggestions)}",
            f"- **High Confidence** (>0.8): {len([s for s in suggestions if s.confidence > 0.8])}",
            f"- **Automated Fixes Available**: {len([s for s in suggestions if s.automated])}",
            "",
            "## Suggested Improvements",
            ""
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            confidence_emoji = "🟢" if suggestion.confidence > 0.8 else "🟡" if suggestion.confidence > 0.6 else "🔴"
            auto_emoji = "🤖" if suggestion.automated else "👤"
            
            report_lines.extend([
                f"### {i}. {suggestion.rewrite_type.value.replace('_', ' ').title()} {confidence_emoji} {auto_emoji}",
                f"**Section**: {suggestion.section}",
                f"**Confidence**: {suggestion.confidence:.2f}",
                f"**Reason**: {suggestion.reason}",
                "",
                "**Original**:",
                f"```markdown",
                suggestion.original_content,
                "```",
                "",
                "**Suggested**:",
                f"```markdown", 
                suggestion.suggested_content,
                "```",
                ""
            ])
        
        # Add execution statistics
        report_lines.extend([
            "## Execution Statistics",
            ""
        ])
        
        success_rate = self._calculate_success_rate(execution_results)
        report_lines.extend([
            f"- **Success Rate**: {success_rate:.1f}%",
            f"- **Total Steps**: {len(execution_results)}",
            f"- **Failed Steps**: {len([r for r in execution_results if not r.get('success', False)])}",
            ""
        ])
        
        return "\n".join(report_lines)
    
    async def _analyze_command_failures(
        self, 
        tutorial_content: str, 
        execution_results: List[Dict[str, Any]]
    ) -> List[TutorialSuggestion]:
        """Analyze command failures and suggest fixes"""
        suggestions = []
        
        for result in execution_results:
            if not result.get('success', False) and 'command' in result:
                command = result['command']
                error = result.get('error_message', '')
                
                # Path resolution suggestions
                if "can't cd to" in error or "No such file or directory" in error:
                    suggestions.append(TutorialSuggestion(
                        rewrite_type=RewriteType.PATH_CORRECTION,
                        section=f"Command: {command[:50]}...",
                        line_number=0,  # Would need to find actual line
                        original_content=command,
                        suggested_content=self._suggest_path_fix(command, error),
                        reason="Fix path resolution issue",
                        confidence=0.9,
                        issue_category=IssueCategory.CONFIGURATION
                    ))
                
                # Container image suggestions
                if "manifest unknown" in error:
                    suggestions.append(TutorialSuggestion(
                        rewrite_type=RewriteType.COMMAND_UPDATE,
                        section=f"Container command",
                        line_number=0,
                        original_content=command,
                        suggested_content=command.replace("ghcr.io/bcda-aps/epics-podman:latest", "epics-podman:latest"),
                        reason="Use local container image instead of remote",
                        confidence=0.95,
                        issue_category=IssueCategory.CONTAINER
                    ))
                
        return suggestions
    
    async def _analyze_successful_fixes(
        self, 
        tutorial_content: str, 
        fixes_applied: List[Fix]
    ) -> List[TutorialSuggestion]:
        """Generate suggestions based on successful fixes"""
        suggestions = []
        
        for fix in fixes_applied:
            if fix.success:
                # If conda initialization was needed, suggest adding it to tutorial
                if "conda" in " ".join(fix.commands):
                    suggestions.append(TutorialSuggestion(
                        rewrite_type=RewriteType.PREREQUISITE_ADD,
                        section="Prerequisites",
                        line_number=0,
                        original_content="",
                        suggested_content=self._generate_conda_prerequisite(),
                        reason="Add conda initialization prerequisite based on execution results",
                        confidence=0.85,
                        issue_category=IssueCategory.ENVIRONMENT
                    ))
                
        return suggestions
    
    async def _analyze_common_patterns(
        self, 
        tutorial_content: str, 
        issues_detected: List[Issue]
    ) -> List[TutorialSuggestion]:
        """Analyze common issue patterns and suggest preventive measures"""
        suggestions = []
        
        # Count issue types
        issue_counts = {}
        for issue in issues_detected:
            category = issue.category.value
            issue_counts[category] = issue_counts.get(category, 0) + 1
        
        # Suggest improvements for common issues
        if issue_counts.get('environment', 0) > 2:
            suggestions.append(TutorialSuggestion(
                rewrite_type=RewriteType.TROUBLESHOOTING_ADD,
                section="Troubleshooting",
                line_number=0,
                original_content="",
                suggested_content=self._generate_environment_troubleshooting(),
                reason="Add environment troubleshooting based on common issues",
                confidence=0.8,
                issue_category=IssueCategory.ENVIRONMENT
            ))
        
        return suggestions
    
    async def _suggest_prerequisites(
        self,
        tutorial_content: str,
        issues_detected: List[Issue]
    ) -> List[TutorialSuggestion]:
        """Suggest missing prerequisites"""
        suggestions = []
        
        # Check for missing software prerequisites
        software_issues = [i for i in issues_detected if "not found" in i.error_message]
        
        for issue in software_issues:
            if "conda" in issue.error_message:
                suggestions.append(TutorialSuggestion(
                    rewrite_type=RewriteType.PREREQUISITE_ADD,
                    section="Prerequisites",
                    line_number=0,
                    original_content="",
                    suggested_content="- **Conda**: Anaconda or Miniconda for environment management",
                    reason="Conda is required but not listed in prerequisites",
                    confidence=0.9
                ))
        
        return suggestions
    
    async def _enhance_troubleshooting(
        self,
        tutorial_content: str,
        issues_detected: List[Issue]
    ) -> List[TutorialSuggestion]:
        """Enhance troubleshooting sections based on actual issues"""
        suggestions = []
        
        troubleshooting_content = self._generate_troubleshooting_section(issues_detected)
        
        if troubleshooting_content:
            suggestions.append(TutorialSuggestion(
                rewrite_type=RewriteType.TROUBLESHOOTING_ADD,
                section="Troubleshooting",
                line_number=0,
                original_content="",
                suggested_content=troubleshooting_content,
                reason="Add troubleshooting section for commonly encountered issues",
                confidence=0.75
            ))
        
        return suggestions
    
    def _suggest_path_fix(self, command: str, error: str) -> str:
        """Suggest fixed paths based on error"""
        if "/path/to/bits_demo" in command:
            return command.replace("/path/to/bits_demo", str(Path.cwd() / "bits_base/BITS/src/bits_demo"))
        elif "bits_demo/" in command:
            return command.replace("bits_demo/", str(Path.cwd() / "bits_base/BITS/src/bits_demo/"))
        elif "containers/epics-podman/" in command:
            return command.replace("containers/epics-podman/", str(Path.cwd() / "containers/epics-podman/"))
        return command
    
    def _generate_conda_prerequisite(self) -> str:
        """Generate conda prerequisite text"""
        return """
#### Conda Environment Setup
Before starting, ensure conda is properly initialized:
```bash
# Initialize conda (run once per system)
conda init bash
source ~/.bashrc

# Verify conda is working
conda --version
```
"""
    
    def _generate_environment_troubleshooting(self) -> str:
        """Generate environment troubleshooting section"""
        return """
## Environment Troubleshooting

### Conda Issues
```bash
# If conda activate fails
source ~/miniconda3/etc/profile.d/conda.sh
# or
source ~/anaconda3/etc/profile.d/conda.sh

# Then try activating again
conda activate BITS_demo
```

### Path Issues
```bash
# If you get "No such file or directory" errors
# Verify you're in the correct directory
pwd
ls -la

# Navigate to the project root
cd /path/to/your/bAIt/project
```
"""
    
    def _generate_troubleshooting_section(self, issues: List[Issue]) -> str:
        """Generate comprehensive troubleshooting section"""
        if not issues:
            return ""
        
        sections = ["## Common Issues & Solutions", ""]
        
        # Group issues by category
        categories = {}
        for issue in issues:
            cat = issue.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(issue)
        
        for category, cat_issues in categories.items():
            sections.append(f"### {category.title()} Issues")
            sections.append("")
            
            for issue in cat_issues[:2]:  # Limit to top 2 per category
                sections.extend([
                    f"**Problem**: {issue.title}",
                    f"**Symptoms**: {issue.error_message[:100]}...",
                    "**Solution**: [Fix would be generated based on successful patterns]",
                    ""
                ])
        
        return "\n".join(sections)
    
    def _calculate_success_rate(self, execution_results: List[Dict[str, Any]]) -> float:
        """Calculate success rate from execution results"""
        if not execution_results:
            return 0.0
        
        successful = sum(1 for r in execution_results if r.get('success', False))
        return (successful / len(execution_results)) * 100
    
    async def _read_tutorial_file(self, file_path: Path) -> str:
        """Read tutorial file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read tutorial file {file_path}: {e}")
            return ""
    
    async def _write_tutorial_file(self, file_path: Path, content: str):
        """Write tutorial file content"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Failed to write tutorial file {file_path}: {e}")
    
    async def _create_backup(self, original_path: Path, backup_path: Path):
        """Create backup of original file"""
        try:
            import shutil
            shutil.copy2(original_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
    
    async def _apply_suggestion(self, content: str, suggestion: TutorialSuggestion) -> str:
        """Apply a single suggestion to content"""
        # Simple implementation - could be enhanced with better matching
        if suggestion.original_content and suggestion.original_content in content:
            return content.replace(suggestion.original_content, suggestion.suggested_content)
        else:
            # For additions, append to appropriate section
            return content + "\n\n" + suggestion.suggested_content