"""
MEDM Analyzer for bAIt.

This analyzer provides analysis of MEDM (Motif Editor Display Manager) screen files
to understand control screen layouts, PV connections, and user interface structure.
"""

import logging
import re
from pathlib import Path
from typing import Any

from .base_analyzer import AnalysisResult, BaseAnalyzer

logger = logging.getLogger(__name__)


class MEDMAnalyzer(BaseAnalyzer):
    """
    Analyzer for MEDM screen files.

    This analyzer examines MEDM .adl files to extract information about
    screen layouts, PV connections, and control elements.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the MEDM analyzer."""
        super().__init__("medm", config)

        # Common MEDM file patterns
        self.screen_patterns = ["*.adl", "**/*.adl"]
        self.backup_patterns = ["*.adl~", "**/*.adl~"]

        # MEDM object types
        self.object_types = {
            "text", "rectangle", "oval", "arc", "line", "polyline", "polygon",
            "text update", "text entry", "menu", "choice button", "message button",
            "related display", "shell command", "wheel switch", "valuator",
            "strip chart", "cartesian plot", "bar", "indicator", "meter",
            "composite", "byte", "image"
        }

    def analyze(self, target: str | Path | dict[str, Any]) -> AnalysisResult:
        """
        Analyze MEDM configuration.

        Args:
            target: MEDM configuration (path to screens directory or config dict)

        Returns:
            AnalysisResult with MEDM analysis
        """
        self._log_analysis_start(target)

        try:
            if isinstance(target, str | Path):
                medm_path = self._resolve_path(target)
                result = self._analyze_medm_directory(medm_path)
            elif isinstance(target, dict):
                result = self._analyze_medm_config(target)
            else:
                return self._create_result(
                    status="error",
                    summary="Invalid target type for MEDM analysis",
                    issues=[self._create_issue("error", f"Unsupported target type: {type(target)}")]
                )

            self._log_analysis_complete(result)
            return result

        except Exception as e:
            self.logger.error(f"Error during MEDM analysis: {e}")
            return self._create_result(
                status="error",
                summary=f"MEDM analysis failed: {str(e)}",
                issues=[self._create_issue("error", f"Analysis exception: {str(e)}")]
            )

    def validate_target(self, target: str | Path | dict[str, Any]) -> bool:
        """
        Validate that the target is a valid MEDM configuration.

        Args:
            target: Target to validate

        Returns:
            True if target is valid
        """
        try:
            if isinstance(target, str | Path):
                medm_path = self._resolve_path(target)
                if not medm_path.exists():
                    return False

                # Check for MEDM files
                return self._has_medm_files(medm_path)

            elif isinstance(target, dict):
                # Check for MEDM configuration structure
                return any(key in target for key in ["screen_folders", "main_screen", "screens"])

            return False

        except Exception:
            return False

    def get_supported_formats(self) -> list[str]:
        """Get supported MEDM file formats."""
        return ["adl"]

    def get_description(self) -> str:
        """Get analyzer description."""
        return "Analyzes MEDM screen files for PV connections, control elements, and interface structure"

    def _analyze_medm_directory(self, medm_path: Path) -> AnalysisResult:
        """Analyze a MEDM screens directory."""
        issues = []
        details = {}
        recommendations = []

        # Basic directory info
        details["medm_path"] = str(medm_path)
        details["exists"] = medm_path.exists()

        if not medm_path.exists():
            issues.append(self._create_issue(
                "error",
                f"MEDM directory not found: {medm_path}",
                location=str(medm_path)
            ))
            return self._create_result(
                status="error",
                summary="MEDM directory not found",
                details=details,
                issues=issues
            )

        # Find screen files
        screen_files = self._find_screen_files(medm_path)
        details["screen_files"] = [str(f) for f in screen_files]
        details["screen_count"] = len(screen_files)

        if not screen_files:
            issues.append(self._create_issue(
                "warning",
                "No MEDM screen files found",
                location=str(medm_path)
            ))
        else:
            # Analyze screen files
            screen_analysis = self._analyze_screen_files(screen_files)
            details["screen_analysis"] = screen_analysis

            # Check for issues
            if screen_analysis["errors"]:
                for error in screen_analysis["errors"]:
                    issues.append(self._create_issue(
                        "error",
                        error,
                        location=str(medm_path)
                    ))

        # Find backup files
        backup_files = self._find_backup_files(medm_path)
        details["backup_files"] = [str(f) for f in backup_files]
        details["backup_count"] = len(backup_files)

        if backup_files:
            recommendations.append(f"Consider cleaning up {len(backup_files)} backup files (.adl~)")

        # Generate recommendations
        if screen_files and len(screen_files) > 50:
            recommendations.append("Large number of screen files - consider organizing into subdirectories")

        if details.get("screen_analysis", {}).get("orphaned_screens"):
            recommendations.append("Found orphaned screens - consider organizing or removing unused screens")

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "MEDM analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "MEDM analysis found warnings"
        else:
            status = "success"
            summary = f"MEDM analysis completed ({len(screen_files)} screen files)"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_medm_config(self, config: dict[str, Any]) -> AnalysisResult:
        """Analyze MEDM configuration from dictionary."""
        issues = []
        details = {}
        recommendations = []

        # Extract basic info
        if "screen_folders" in config:
            details["screen_folders"] = config["screen_folders"]
            details["folder_count"] = len(config["screen_folders"])

        if "main_screen" in config:
            details["main_screen"] = config["main_screen"]

        # Check for required fields
        if "screen_folders" not in config and "screens" not in config:
            issues.append(self._create_issue(
                "warning",
                "No screen_folders or screens specified in MEDM configuration",
                location="config"
            ))
            recommendations.append("Add screen_folders or screens to MEDM configuration")

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "MEDM configuration analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "MEDM configuration analysis found warnings"
        else:
            status = "success"
            summary = "MEDM configuration analysis completed"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _has_medm_files(self, path: Path) -> bool:
        """Check if directory contains MEDM files."""
        for pattern in self.screen_patterns:
            if list(path.glob(pattern)):
                return True
        return False

    def _find_screen_files(self, medm_path: Path) -> list[Path]:
        """Find MEDM screen files."""
        screen_files = []

        for pattern in self.screen_patterns:
            files = self._find_files(medm_path, pattern)
            screen_files.extend(files)

        return screen_files

    def _find_backup_files(self, medm_path: Path) -> list[Path]:
        """Find MEDM backup files."""
        backup_files = []

        for pattern in self.backup_patterns:
            files = self._find_files(medm_path, pattern)
            backup_files.extend(files)

        return backup_files

    def _analyze_screen_files(self, screen_files: list[Path]) -> dict[str, Any]:
        """Analyze MEDM screen files."""
        analysis = {
            "total_files": len(screen_files),
            "total_objects": 0,
            "object_types": {},
            "pv_connections": [],
            "unique_pvs": set(),
            "screen_relationships": {},
            "orphaned_screens": [],
            "errors": []
        }

        for screen_file in screen_files:
            try:
                screen_analysis = self._analyze_single_screen(screen_file)

                # Aggregate data
                analysis["total_objects"] += screen_analysis["object_count"]

                # Count object types
                for obj_type, count in screen_analysis["object_types"].items():
                    if obj_type not in analysis["object_types"]:
                        analysis["object_types"][obj_type] = 0
                    analysis["object_types"][obj_type] += count

                # Collect PV connections
                for pv in screen_analysis["pvs"]:
                    analysis["pv_connections"].append({
                        "screen": screen_file.name,
                        "pv": pv
                    })
                    analysis["unique_pvs"].add(pv)

                # Track screen relationships
                if screen_analysis["related_displays"]:
                    analysis["screen_relationships"][screen_file.name] = screen_analysis["related_displays"]

                # Check for orphaned screens (no related displays pointing to them)
                if not screen_analysis["related_displays"] and screen_file.name not in analysis["screen_relationships"]:
                    analysis["orphaned_screens"].append(screen_file.name)

            except Exception as e:
                analysis["errors"].append(f"Error analyzing screen {screen_file}: {e}")

        # Convert set to list for JSON serialization
        analysis["unique_pvs"] = list(analysis["unique_pvs"])
        analysis["unique_pv_count"] = len(analysis["unique_pvs"])

        return analysis

    def _analyze_single_screen(self, screen_file: Path) -> dict[str, Any]:
        """Analyze a single MEDM screen file."""
        analysis = {
            "file": str(screen_file),
            "object_count": 0,
            "object_types": {},
            "pvs": [],
            "related_displays": [],
            "colors": [],
            "dimensions": {},
            "errors": []
        }

        try:
            content = self._read_file(screen_file)

            # Parse ADL file structure
            analysis.update(self._parse_adl_content(content))

        except Exception as e:
            analysis["errors"].append(f"Error reading screen file: {e}")

        return analysis

    def _parse_adl_content(self, content: str) -> dict[str, Any]:
        """Parse MEDM ADL file content."""
        analysis = {
            "object_count": 0,
            "object_types": {},
            "pvs": [],
            "related_displays": [],
            "colors": [],
            "dimensions": {}
        }

        lines = content.splitlines()
        current_object = None
        brace_depth = 0

        for _line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Track brace depth
            brace_depth += line.count('{') - line.count('}')

            # Look for object definitions
            if line.startswith('object'):
                # Extract object type
                match = re.match(r'object\s*\{\s*(\w+.*?)\s*\}', line)
                if match:
                    current_object = match.group(1).strip()
                    analysis["object_count"] += 1

                    if current_object not in analysis["object_types"]:
                        analysis["object_types"][current_object] = 0
                    analysis["object_types"][current_object] += 1

            # Look for PV names
            pv_patterns = [
                r'chan="([^"]+)"',
                r'rdbk="([^"]+)"',
                r'ctrl="([^"]+)"',
                r'readPv="([^"]+)"',
                r'writePv="([^"]+)"'
            ]

            for pattern in pv_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if match and match not in analysis["pvs"]:
                        analysis["pvs"].append(match)

            # Look for related displays
            if 'display[' in line:
                display_match = re.search(r'display\[\d+\]\s*\{\s*label="([^"]+)"\s*name="([^"]+)"', line)
                if display_match:
                    analysis["related_displays"].append({
                        "label": display_match.group(1),
                        "name": display_match.group(2)
                    })

            # Look for color definitions
            if line.startswith('color'):
                color_match = re.search(r'color=(\d+)', line)
                if color_match:
                    analysis["colors"].append(int(color_match.group(1)))

            # Look for display dimensions
            if line.startswith('display'):
                width_match = re.search(r'width=(\d+)', line)
                height_match = re.search(r'height=(\d+)', line)
                if width_match:
                    analysis["dimensions"]["width"] = int(width_match.group(1))
                if height_match:
                    analysis["dimensions"]["height"] = int(height_match.group(1))

        return analysis
