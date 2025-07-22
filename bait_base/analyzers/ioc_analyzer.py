"""
IOC Analyzer for bAIt.

This analyzer provides analysis of EPICS IOC configurations including
database files, startup scripts, and configuration parameters.
"""

import logging
import re
from pathlib import Path
from typing import Any

from .base_analyzer import AnalysisResult, BaseAnalyzer

logger = logging.getLogger(__name__)


class IOCAnalyzer(BaseAnalyzer):
    """
    Analyzer for EPICS IOC configurations.

    This analyzer examines IOC startup scripts, database files, and
    configuration parameters to provide insights about IOC setup and health.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the IOC analyzer."""
        super().__init__("ioc", config)

        # Common IOC file patterns
        self.startup_patterns = ["st.cmd", "startup.cmd", "iocBoot/*/*.cmd"]
        self.database_patterns = ["*.db", "*.template", "*.substitutions"]
        self.config_patterns = ["*.cfg", "*.ini", "*.conf"]

    def analyze(self, target: str | Path | dict[str, Any]) -> AnalysisResult:
        """
        Analyze IOC configuration.

        Args:
            target: IOC configuration (path to IOC directory or config dict)

        Returns:
            AnalysisResult with IOC analysis
        """
        self._log_analysis_start(target)

        try:
            if isinstance(target, str | Path):
                ioc_path = self._resolve_path(target)
                result = self._analyze_ioc_directory(ioc_path)
            elif isinstance(target, dict):
                result = self._analyze_ioc_config(target)
            else:
                return self._create_result(
                    status="error",
                    summary="Invalid target type for IOC analysis",
                    issues=[self._create_issue("error", f"Unsupported target type: {type(target)}")]
                )

            self._log_analysis_complete(result)
            return result

        except Exception as e:
            self.logger.error(f"Error during IOC analysis: {e}")
            return self._create_result(
                status="error",
                summary=f"IOC analysis failed: {str(e)}",
                issues=[self._create_issue("error", f"Analysis exception: {str(e)}")]
            )

    def validate_target(self, target: str | Path | dict[str, Any]) -> bool:
        """
        Validate that the target is a valid IOC configuration.

        Args:
            target: Target to validate

        Returns:
            True if target is valid
        """
        try:
            if isinstance(target, str | Path):
                ioc_path = self._resolve_path(target)
                if not ioc_path.exists():
                    return False

                # Check for IOC-specific files
                return self._has_ioc_files(ioc_path)

            elif isinstance(target, dict):
                # Check for IOC configuration structure
                return "name" in target or "startup_file" in target

            return False

        except Exception:
            return False

    def get_supported_formats(self) -> list[str]:
        """Get supported IOC file formats."""
        return ["cmd", "db", "template", "substitutions", "cfg", "ini", "conf"]

    def get_description(self) -> str:
        """Get analyzer description."""
        return "Analyzes EPICS IOC configurations including startup scripts, database files, and parameters"

    def _analyze_ioc_directory(self, ioc_path: Path) -> AnalysisResult:
        """Analyze an IOC directory structure."""
        issues = []
        details = {}
        recommendations = []

        # Basic directory info
        details["ioc_path"] = str(ioc_path)
        details["exists"] = ioc_path.exists()

        if not ioc_path.exists():
            issues.append(self._create_issue(
                "error",
                f"IOC directory not found: {ioc_path}",
                location=str(ioc_path)
            ))
            return self._create_result(
                status="error",
                summary="IOC directory not found",
                details=details,
                issues=issues
            )

        # Find startup files
        startup_files = self._find_startup_files(ioc_path)
        details["startup_files"] = [str(f) for f in startup_files]

        if not startup_files:
            issues.append(self._create_issue(
                "warning",
                "No startup files found",
                location=str(ioc_path)
            ))
        else:
            # Analyze startup files
            for startup_file in startup_files:
                startup_analysis = self._analyze_startup_file(startup_file)
                details[f"startup_{startup_file.name}"] = startup_analysis

        # Find database files
        database_files = self._find_database_files(ioc_path)
        details["database_files"] = [str(f) for f in database_files]
        details["database_count"] = len(database_files)

        if not database_files:
            issues.append(self._create_issue(
                "warning",
                "No database files found",
                location=str(ioc_path)
            ))
        else:
            # Analyze database files
            pv_analysis = self._analyze_database_files(database_files)
            details["pv_analysis"] = pv_analysis

        # Generate recommendations
        if not startup_files and not database_files:
            recommendations.append("Verify IOC directory structure - no IOC files found")

        if len(startup_files) > 1:
            recommendations.append("Multiple startup files found - verify which one is active")

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "IOC analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "IOC analysis found warnings"
        else:
            status = "success"
            summary = f"IOC analysis completed successfully ({len(startup_files)} startup, {len(database_files)} database files)"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_ioc_config(self, config: dict[str, Any]) -> AnalysisResult:
        """Analyze IOC configuration from dictionary."""
        issues = []
        details = {}
        recommendations = []

        # Extract basic info
        details["name"] = config.get("name", "unknown")
        details["description"] = config.get("description", "")

        # Check for required fields
        if "startup_file" not in config:
            issues.append(self._create_issue(
                "warning",
                "No startup_file specified in IOC configuration",
                location="config"
            ))
            recommendations.append("Add startup_file to IOC configuration")

        if "database_files" not in config:
            issues.append(self._create_issue(
                "warning",
                "No database_files specified in IOC configuration",
                location="config"
            ))
            recommendations.append("Add database_files to IOC configuration")

        # Analyze specified files if they exist
        if "database_files" in config:
            details["database_files"] = config["database_files"]
            details["database_count"] = len(config["database_files"])

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "IOC configuration analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "IOC configuration analysis found warnings"
        else:
            status = "success"
            summary = f"IOC configuration analysis completed for {details['name']}"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _has_ioc_files(self, path: Path) -> bool:
        """Check if directory contains IOC files."""
        # Look for startup files
        for pattern in self.startup_patterns:
            if list(path.glob(pattern)):
                return True

        # Look for database files
        for pattern in self.database_patterns:
            if list(path.glob(pattern)):
                return True

        return False

    def _find_startup_files(self, ioc_path: Path) -> list[Path]:
        """Find IOC startup files."""
        startup_files = []

        for pattern in self.startup_patterns:
            files = self._find_files(ioc_path, pattern)
            startup_files.extend(files)

        return startup_files

    def _find_database_files(self, ioc_path: Path) -> list[Path]:
        """Find IOC database files."""
        database_files = []

        for pattern in self.database_patterns:
            files = self._find_files(ioc_path, pattern)
            database_files.extend(files)

        return database_files

    def _analyze_startup_file(self, startup_file: Path) -> dict[str, Any]:
        """Analyze an IOC startup file."""
        analysis = {
            "file": str(startup_file),
            "exists": startup_file.exists(),
            "size": 0,
            "lines": 0,
            "commands": [],
            "database_loads": [],
            "errors": []
        }

        if not startup_file.exists():
            analysis["errors"].append(f"Startup file not found: {startup_file}")
            return analysis

        try:
            content = self._read_file(startup_file)
            lines = content.splitlines()

            analysis["size"] = len(content)
            analysis["lines"] = len(lines)

            # Parse startup file commands
            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Look for common IOC commands
                if line.startswith('dbLoadRecords'):
                    analysis["database_loads"].append({
                        "line": line_num,
                        "command": line
                    })
                elif any(line.startswith(cmd) for cmd in ['iocInit', 'dbLoadDatabase', 'cd']):
                    analysis["commands"].append({
                        "line": line_num,
                        "command": line
                    })

        except Exception as e:
            analysis["errors"].append(f"Error reading startup file: {e}")

        return analysis

    def _analyze_database_files(self, database_files: list[Path]) -> dict[str, Any]:
        """Analyze IOC database files."""
        analysis = {
            "total_files": len(database_files),
            "total_records": 0,
            "record_types": {},
            "pv_names": [],
            "errors": []
        }

        for db_file in database_files:
            try:
                content = self._read_file(db_file)

                # Simple regex to find record definitions
                record_pattern = r'record\s*\(\s*(\w+)\s*,\s*["\']([^"\']+)["\']'
                matches = re.findall(record_pattern, content, re.IGNORECASE)

                for record_type, pv_name in matches:
                    analysis["total_records"] += 1
                    analysis["pv_names"].append(pv_name)

                    if record_type not in analysis["record_types"]:
                        analysis["record_types"][record_type] = 0
                    analysis["record_types"][record_type] += 1

            except Exception as e:
                analysis["errors"].append(f"Error reading database file {db_file}: {e}")

        return analysis
