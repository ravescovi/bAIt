"""
Bluesky Analyzer for bAIt.

This analyzer provides analysis of Bluesky device configurations, startup files,
and plan definitions to understand the instrument setup and capabilities.
"""

import ast
import logging
from pathlib import Path
from typing import Any

import yaml

from .base_analyzer import AnalysisResult, BaseAnalyzer

logger = logging.getLogger(__name__)


class BlueskyAnalyzer(BaseAnalyzer):
    """
    Analyzer for Bluesky instrument configurations.

    This analyzer examines Bluesky device configurations, startup scripts,
    and plan definitions to provide insights about the instrument setup.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Bluesky analyzer."""
        super().__init__("bluesky", config)

        # Common Bluesky file patterns
        self.startup_patterns = ["startup.py", "*/startup.py", "src/*/startup.py"]
        self.config_patterns = ["*.yml", "*.yaml", "configs/*.yml", "configs/*.yaml"]
        self.plan_patterns = ["plans/*.py", "*/plans/*.py", "src/*/plans/*.py"]
        self.device_patterns = ["devices/*.py", "*/devices/*.py", "src/*/devices/*.py"]

    def analyze(self, target: str | Path | dict[str, Any]) -> AnalysisResult:
        """
        Analyze Bluesky configuration.

        Args:
            target: Bluesky configuration (path to deployment or config dict)

        Returns:
            AnalysisResult with Bluesky analysis
        """
        self._log_analysis_start(target)

        try:
            if isinstance(target, str | Path):
                bluesky_path = self._resolve_path(target)
                result = self._analyze_bluesky_directory(bluesky_path)
            elif isinstance(target, dict):
                result = self._analyze_bluesky_config(target)
            else:
                return self._create_result(
                    status="error",
                    summary="Invalid target type for Bluesky analysis",
                    issues=[self._create_issue("error", f"Unsupported target type: {type(target)}")]
                )

            self._log_analysis_complete(result)
            return result

        except Exception as e:
            self.logger.error(f"Error during Bluesky analysis: {e}")
            return self._create_result(
                status="error",
                summary=f"Bluesky analysis failed: {str(e)}",
                issues=[self._create_issue("error", f"Analysis exception: {str(e)}")]
            )

    def validate_target(self, target: str | Path | dict[str, Any]) -> bool:
        """
        Validate that the target is a valid Bluesky configuration.

        Args:
            target: Target to validate

        Returns:
            True if target is valid
        """
        try:
            if isinstance(target, str | Path):
                bluesky_path = self._resolve_path(target)
                if not bluesky_path.exists():
                    return False

                # Check for Bluesky-specific files
                return self._has_bluesky_files(bluesky_path)

            elif isinstance(target, dict):
                # Check for Bluesky configuration structure
                return any(key in target for key in ["startup_file", "config_files", "devices", "plans"])

            return False

        except Exception:
            return False

    def get_supported_formats(self) -> list[str]:
        """Get supported Bluesky file formats."""
        return ["py", "yml", "yaml"]

    def get_description(self) -> str:
        """Get analyzer description."""
        return "Analyzes Bluesky instrument configurations including devices, plans, and startup files"

    def _analyze_bluesky_directory(self, bluesky_path: Path) -> AnalysisResult:
        """Analyze a Bluesky deployment directory."""
        issues = []
        details = {}
        recommendations = []

        # Basic directory info
        details["bluesky_path"] = str(bluesky_path)
        details["exists"] = bluesky_path.exists()

        if not bluesky_path.exists():
            issues.append(self._create_issue(
                "error",
                f"Bluesky directory not found: {bluesky_path}",
                location=str(bluesky_path)
            ))
            return self._create_result(
                status="error",
                summary="Bluesky directory not found",
                details=details,
                issues=issues
            )

        # Find startup files
        startup_files = self._find_startup_files(bluesky_path)
        details["startup_files"] = [str(f) for f in startup_files]

        if not startup_files:
            issues.append(self._create_issue(
                "warning",
                "No startup files found",
                location=str(bluesky_path)
            ))
        else:
            # Analyze startup files
            for startup_file in startup_files:
                startup_analysis = self._analyze_startup_file(startup_file)
                details[f"startup_{startup_file.stem}"] = startup_analysis

        # Find configuration files
        config_files = self._find_config_files(bluesky_path)
        details["config_files"] = [str(f) for f in config_files]

        if config_files:
            # Analyze configuration files
            config_analysis = self._analyze_config_files(config_files)
            details["config_analysis"] = config_analysis

        # Find device files
        device_files = self._find_device_files(bluesky_path)
        details["device_files"] = [str(f) for f in device_files]

        if device_files:
            # Analyze device files
            device_analysis = self._analyze_device_files(device_files)
            details["device_analysis"] = device_analysis

        # Find plan files
        plan_files = self._find_plan_files(bluesky_path)
        details["plan_files"] = [str(f) for f in plan_files]

        if plan_files:
            # Analyze plan files
            plan_analysis = self._analyze_plan_files(plan_files)
            details["plan_analysis"] = plan_analysis

        # Generate recommendations
        if not startup_files and not config_files:
            recommendations.append("No Bluesky files found - verify deployment structure")

        if not device_files:
            recommendations.append("No device files found - consider organizing devices in separate files")

        if not plan_files:
            recommendations.append("No plan files found - consider creating custom plans")

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "Bluesky analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "Bluesky analysis found warnings"
        else:
            status = "success"
            summary = f"Bluesky analysis completed ({len(startup_files)} startup, {len(config_files)} config, {len(device_files)} device, {len(plan_files)} plan files)"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_bluesky_config(self, config: dict[str, Any]) -> AnalysisResult:
        """Analyze Bluesky configuration from dictionary."""
        issues = []
        details = {}
        recommendations = []

        # Extract basic info
        details["startup_file"] = config.get("startup_file", "unknown")
        details["config_files"] = config.get("config_files", [])

        # Check for required fields
        if "startup_file" not in config:
            issues.append(self._create_issue(
                "warning",
                "No startup_file specified in Bluesky configuration",
                location="config"
            ))
            recommendations.append("Add startup_file to Bluesky configuration")

        if "config_files" not in config:
            issues.append(self._create_issue(
                "info",
                "No config_files specified in Bluesky configuration",
                location="config"
            ))
            recommendations.append("Consider adding config_files to Bluesky configuration")

        # Analyze file counts
        details["config_file_count"] = len(config.get("config_files", []))

        # Determine status
        if any(issue["severity"] == "error" for issue in issues):
            status = "error"
            summary = "Bluesky configuration analysis found errors"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
            summary = "Bluesky configuration analysis found warnings"
        else:
            status = "success"
            summary = "Bluesky configuration analysis completed"

        return self._create_result(
            status=status,
            summary=summary,
            details=details,
            issues=issues,
            recommendations=recommendations
        )

    def _has_bluesky_files(self, path: Path) -> bool:
        """Check if directory contains Bluesky files."""
        # Look for startup files
        for pattern in self.startup_patterns:
            if list(path.glob(pattern)):
                return True

        # Look for config files
        for pattern in self.config_patterns:
            if list(path.glob(pattern)):
                return True

        # Look for device files
        for pattern in self.device_patterns:
            if list(path.glob(pattern)):
                return True

        return False

    def _find_startup_files(self, bluesky_path: Path) -> list[Path]:
        """Find Bluesky startup files."""
        startup_files = []

        for pattern in self.startup_patterns:
            files = self._find_files(bluesky_path, pattern)
            startup_files.extend(files)

        return startup_files

    def _find_config_files(self, bluesky_path: Path) -> list[Path]:
        """Find Bluesky configuration files."""
        config_files = []

        for pattern in self.config_patterns:
            files = self._find_files(bluesky_path, pattern)
            config_files.extend(files)

        return config_files

    def _find_device_files(self, bluesky_path: Path) -> list[Path]:
        """Find Bluesky device files."""
        device_files = []

        for pattern in self.device_patterns:
            files = self._find_files(bluesky_path, pattern)
            device_files.extend(files)

        return device_files

    def _find_plan_files(self, bluesky_path: Path) -> list[Path]:
        """Find Bluesky plan files."""
        plan_files = []

        for pattern in self.plan_patterns:
            files = self._find_files(bluesky_path, pattern)
            plan_files.extend(files)

        return plan_files

    def _analyze_startup_file(self, startup_file: Path) -> dict[str, Any]:
        """Analyze a Bluesky startup file."""
        analysis = {
            "file": str(startup_file),
            "exists": startup_file.exists(),
            "size": 0,
            "lines": 0,
            "imports": [],
            "devices": [],
            "plans": [],
            "callbacks": [],
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

            # Parse Python file for imports and device/plan definitions
            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")
                    elif isinstance(node, ast.Assign):
                        # Look for device assignments
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Simple heuristic: if it looks like a device assignment
                                if any(keyword in str(node.value) for keyword in ["EpicsMotor", "EpicsSignal", "Device"]):
                                    analysis["devices"].append(target.id)
                    elif isinstance(node, ast.FunctionDef):
                        # Look for plan definitions
                        if any(decorator.id == "bpp.run_decorator" for decorator in node.decorator_list
                               if isinstance(decorator, ast.Name)):
                            analysis["plans"].append(node.name)
                        elif node.name.endswith("_plan") or node.name.startswith("plan_"):
                            analysis["plans"].append(node.name)

            except SyntaxError as e:
                analysis["errors"].append(f"Syntax error in startup file: {e}")

        except Exception as e:
            analysis["errors"].append(f"Error reading startup file: {e}")

        return analysis

    def _analyze_config_files(self, config_files: list[Path]) -> dict[str, Any]:
        """Analyze Bluesky configuration files."""
        analysis = {
            "total_files": len(config_files),
            "device_configs": {},
            "callback_configs": {},
            "general_configs": {},
            "errors": []
        }

        for config_file in config_files:
            try:
                content = self._read_file(config_file)

                # Parse YAML content
                if config_file.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(content)

                    if isinstance(config_data, dict):
                        # Look for device configurations
                        if "devices" in config_data:
                            analysis["device_configs"][config_file.name] = config_data["devices"]

                        # Look for callback configurations
                        if "callbacks" in config_data:
                            analysis["callback_configs"][config_file.name] = config_data["callbacks"]

                        # Store general configuration
                        analysis["general_configs"][config_file.name] = {
                            "keys": list(config_data.keys()),
                            "structure": self._analyze_dict_structure(config_data)
                        }

            except Exception as e:
                analysis["errors"].append(f"Error reading config file {config_file}: {e}")

        return analysis

    def _analyze_device_files(self, device_files: list[Path]) -> dict[str, Any]:
        """Analyze Bluesky device files."""
        analysis = {
            "total_files": len(device_files),
            "device_classes": [],
            "imported_devices": [],
            "custom_devices": [],
            "errors": []
        }

        for device_file in device_files:
            try:
                content = self._read_file(device_file)

                # Parse Python file for device definitions
                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Look for device class definitions
                            if any(base.id in ["Device", "EpicsDevice"]
                                   for base in node.bases if isinstance(base, ast.Name)):
                                analysis["custom_devices"].append(node.name)
                            analysis["device_classes"].append(node.name)
                        elif isinstance(node, ast.ImportFrom):
                            # Look for imported device types
                            if node.module and "ophyd" in node.module:
                                for alias in node.names:
                                    analysis["imported_devices"].append(alias.name)

                except SyntaxError as e:
                    analysis["errors"].append(f"Syntax error in device file {device_file}: {e}")

            except Exception as e:
                analysis["errors"].append(f"Error reading device file {device_file}: {e}")

        return analysis

    def _analyze_plan_files(self, plan_files: list[Path]) -> dict[str, Any]:
        """Analyze Bluesky plan files."""
        analysis = {
            "total_files": len(plan_files),
            "plan_functions": [],
            "imported_plans": [],
            "custom_plans": [],
            "errors": []
        }

        for plan_file in plan_files:
            try:
                content = self._read_file(plan_file)

                # Parse Python file for plan definitions
                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            analysis["plan_functions"].append(node.name)

                            # Check if it's a custom plan (has yield statements)
                            for child in ast.walk(node):
                                if isinstance(child, ast.Yield) or isinstance(child, ast.YieldFrom):
                                    analysis["custom_plans"].append(node.name)
                                    break
                        elif isinstance(node, ast.ImportFrom):
                            # Look for imported plan types
                            if node.module and "bluesky" in node.module:
                                for alias in node.names:
                                    analysis["imported_plans"].append(alias.name)

                except SyntaxError as e:
                    analysis["errors"].append(f"Syntax error in plan file {plan_file}: {e}")

            except Exception as e:
                analysis["errors"].append(f"Error reading plan file {plan_file}: {e}")

        return analysis

    def _analyze_dict_structure(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze the structure of a dictionary."""
        structure = {
            "total_keys": len(data),
            "key_types": {},
            "nested_levels": 0
        }

        for _key, value in data.items():
            value_type = type(value).__name__
            if value_type not in structure["key_types"]:
                structure["key_types"][value_type] = 0
            structure["key_types"][value_type] += 1

            if isinstance(value, dict):
                structure["nested_levels"] = max(structure["nested_levels"], 1)

        return structure
