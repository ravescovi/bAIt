"""
Base analyzer interface and common functionality for bAIt analyzers.

This module provides the abstract base class and common utilities that all
bAIt analyzers should inherit from to ensure consistent behavior and interfaces.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AnalysisResult(BaseModel):
    """Standard analysis result structure."""

    analyzer_name: str = Field(..., description="Name of the analyzer that generated this result")
    timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    status: str = Field(..., description="Analysis status: success, warning, error")
    summary: str = Field(..., description="Brief summary of analysis results")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed analysis results")
    issues: list[dict[str, Any]] = Field(default_factory=list, description="List of issues found")
    recommendations: list[str] = Field(default_factory=list, description="Recommended actions")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Analysis metrics")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()

    def has_errors(self) -> bool:
        """Check if analysis found any errors."""
        return any(issue.get("severity") == "error" for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if analysis found any warnings."""
        return any(issue.get("severity") == "warning" for issue in self.issues)


class BaseAnalyzer(ABC):
    """Abstract base class for all bAIt analyzers."""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        """
        Initialize the analyzer.

        Args:
            name: Name of the analyzer
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"bait.analyzers.{name}")

    @abstractmethod
    def analyze(self, target: str | Path | dict[str, Any]) -> AnalysisResult:
        """
        Perform analysis on the target.

        Args:
            target: Target to analyze (path, configuration, etc.)

        Returns:
            AnalysisResult containing analysis findings
        """
        pass

    @abstractmethod
    def validate_target(self, target: str | Path | dict[str, Any]) -> bool:
        """
        Validate that the target is appropriate for this analyzer.

        Args:
            target: Target to validate

        Returns:
            True if target is valid for this analyzer
        """
        pass

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported file formats/extensions.

        Returns:
            List of supported formats
        """
        return []

    def get_description(self) -> str:
        """
        Get human-readable description of what this analyzer does.

        Returns:
            Description string
        """
        return f"Base analyzer: {self.name}"

    def _create_result(
        self,
        status: str,
        summary: str,
        details: dict[str, Any] | None = None,
        issues: list[dict[str, Any]] | None = None,
        recommendations: list[str] | None = None,
        metrics: dict[str, Any] | None = None
    ) -> AnalysisResult:
        """
        Create a standardized analysis result.

        Args:
            status: Analysis status
            summary: Brief summary
            details: Detailed results
            issues: List of issues found
            recommendations: Recommended actions
            metrics: Analysis metrics

        Returns:
            AnalysisResult object
        """
        return AnalysisResult(
            analyzer_name=self.name,
            status=status,
            summary=summary,
            details=details or {},
            issues=issues or [],
            recommendations=recommendations or [],
            metrics=metrics or {}
        )

    def _create_issue(
        self,
        severity: str,
        message: str,
        location: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create a standardized issue dictionary.

        Args:
            severity: Issue severity (error, warning, info)
            message: Issue description
            location: Location where issue was found
            code: Issue code/identifier
            details: Additional issue details

        Returns:
            Issue dictionary
        """
        issue = {
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        if location:
            issue["location"] = location
        if code:
            issue["code"] = code
        if details:
            issue["details"] = details

        return issue

    def _resolve_path(self, path: str | Path) -> Path:
        """
        Resolve a path to a Path object.

        Args:
            path: Path to resolve

        Returns:
            Path object
        """
        return Path(path).resolve()

    def _read_file(self, path: str | Path) -> str:
        """
        Read file content safely.

        Args:
            path: Path to file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: {resolved_path}")

        if not resolved_path.is_file():
            raise OSError(f"Path is not a file: {resolved_path}")

        try:
            return resolved_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            return resolved_path.read_text(encoding='latin-1')

    def _read_json(self, path: str | Path) -> dict[str, Any]:
        """
        Read JSON file safely.

        Args:
            path: Path to JSON file

        Returns:
            Parsed JSON data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        content = self._read_file(path)
        return json.loads(content)

    def _find_files(
        self,
        base_path: str | Path,
        pattern: str,
        recursive: bool = True
    ) -> list[Path]:
        """
        Find files matching a pattern.

        Args:
            base_path: Base directory to search
            pattern: Glob pattern to match
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        resolved_path = self._resolve_path(base_path)

        if not resolved_path.exists():
            return []

        if not resolved_path.is_dir():
            return []

        if recursive:
            return list(resolved_path.rglob(pattern))
        else:
            return list(resolved_path.glob(pattern))

    def _log_analysis_start(self, target: str | Path | dict[str, Any]) -> None:
        """Log analysis start."""
        self.logger.info(f"Starting analysis of {target}")

    def _log_analysis_complete(self, result: AnalysisResult) -> None:
        """Log analysis completion."""
        self.logger.info(
            f"Analysis complete: {result.status} - {result.summary} "
            f"({len(result.issues)} issues, {len(result.recommendations)} recommendations)"
        )
