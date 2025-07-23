#!/usr/bin/env python3
"""
BITS Tutorial Test Agent CLI

Command-line interface for running the automated BITS tutorial testing system.
"""

import argparse
import asyncio
import json
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add bait_base to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "bait_base"))

from agents.specialized.tutorial_test_agent import TutorialTestAgent


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None):
    """Setup logging configuration"""
    level = getattr(logging, log_level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "bait_base" / "config" / "tutorial_test_config.yaml"
    
    if not config_path.exists():
        print(f"Warning: Config file not found at {config_path}")
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_report(result: Dict[str, Any], output_dir: Path, formats: List[str]):
    """Save test report in specified formats"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for unique filenames
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for format_type in formats:
        if format_type == "json":
            output_file = output_dir / f"tutorial_test_report_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"JSON report saved: {output_file}")
            
        elif format_type == "html":
            output_file = output_dir / f"tutorial_test_report_{timestamp}.html"
            html_content = generate_html_report(result)
            with open(output_file, 'w') as f:
                f.write(html_content)
            print(f"HTML report saved: {output_file}")
            
        elif format_type == "text":
            output_file = output_dir / f"tutorial_test_report_{timestamp}.txt"
            text_content = generate_text_report(result)
            with open(output_file, 'w') as f:
                f.write(text_content)
            print(f"Text report saved: {output_file}")


def generate_html_report(result: Dict[str, Any]) -> str:
    """Generate HTML report from test results"""
    test_run = result.get("test_run", {})
    report = result.get("report", {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BITS Tutorial Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .warning {{ color: orange; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .step-details {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>BITS Tutorial Test Report</h1>
            <p><strong>Run ID:</strong> {test_run.get('run_id', 'N/A')}</p>
            <p><strong>Timestamp:</strong> {test_run.get('start_time', 'N/A')}</p>
            <p><strong>Environment:</strong> {test_run.get('environment', {}).get('os', 'N/A')}</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <p class="{'success' if result.get('success') else 'failure'}">
                <strong>Overall Status:</strong> {'PASSED' if result.get('success') else 'FAILED'}
            </p>
            <p><strong>Success Rate:</strong> {result.get('success_rate', 0)*100:.1f}%</p>
            <p><strong>Steps Passed:</strong> {test_run.get('steps_passed', 0)}</p>
            <p><strong>Steps Failed:</strong> {test_run.get('steps_failed', 0)}</p>
            <p><strong>Total Execution Time:</strong> {test_run.get('total_execution_time', 0):.1f}s</p>
        </div>
        
        <div class="issues">
            <h2>Issues Summary</h2>
            <p><strong>Total Issues:</strong> {report.get('issues_summary', {}).get('total_issues', 0)}</p>
            <p><strong>Critical Issues:</strong> {report.get('issues_summary', {}).get('critical_issues', 0)}</p>
            <p><strong>Fixes Applied:</strong> {report.get('issues_summary', {}).get('fixes_applied', 0)}</p>
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            <ul>
    """
    
    for rec in report.get('recommendations', []):
        html += f"<li>{rec}</li>"
    
    html += """
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_text_report(result: Dict[str, Any]) -> str:
    """Generate text report from test results"""
    test_run = result.get("test_run", {})
    report = result.get("report", {})
    
    text = f"""
BITS Tutorial Test Report
========================

Run Information:
- Run ID: {test_run.get('run_id', 'N/A')}
- Start Time: {test_run.get('start_time', 'N/A')}
- Environment: {test_run.get('environment', {}).get('os', 'N/A')}

Summary:
- Overall Status: {'PASSED' if result.get('success') else 'FAILED'}
- Success Rate: {result.get('success_rate', 0)*100:.1f}%
- Steps Passed: {test_run.get('steps_passed', 0)}
- Steps Failed: {test_run.get('steps_failed', 0)}
- Total Execution Time: {test_run.get('total_execution_time', 0):.1f}s

Issues Summary:
- Total Issues: {report.get('issues_summary', {}).get('total_issues', 0)}
- Critical Issues: {report.get('issues_summary', {}).get('critical_issues', 0)}
- Fixes Applied: {report.get('issues_summary', {}).get('fixes_applied', 0)}

Recommendations:
"""
    
    for rec in report.get('recommendations', []):
        text += f"- {rec}\n"
    
    return text


def print_summary(result: Dict[str, Any]):
    """Print a summary of test results to console"""
    test_run = result.get("test_run", {})
    success = result.get("success", False)
    
    print("\n" + "="*60)
    print("BITS TUTORIAL TEST SUMMARY")
    print("="*60)
    print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"Success Rate: {result.get('success_rate', 0)*100:.1f}%")
    print(f"Steps Passed: {test_run.get('steps_passed', 0)}")
    print(f"Steps Failed: {test_run.get('steps_failed', 0)}")
    print(f"Execution Time: {test_run.get('total_execution_time', 0):.1f}s")
    
    # Show issues if any
    issues_detected = len(test_run.get('issues_detected', []))
    fixes_applied = len(test_run.get('fixes_applied', []))
    
    if issues_detected > 0:
        print(f"\nIssues Detected: {issues_detected}")
        print(f"Fixes Applied: {fixes_applied}")
    
    print("="*60)


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="BITS Tutorial Test Agent - Automated tutorial validation"
    )
    
    # Basic options
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--tutorial-files", "-t",
        nargs="+",
        help="Specific tutorial files to test"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("tutorial_test_reports"),
        help="Output directory for reports"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path"
    )
    
    # Test behavior options
    parser.add_argument(
        "--clean-env",
        action="store_true",
        default=True,
        help="Start with clean environment"
    )
    
    parser.add_argument(
        "--no-clean-env",
        action="store_false",
        dest="clean_env",
        help="Don't clean environment before testing"
    )
    
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop testing on first failure"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        help="Maximum retry attempts per step"
    )
    
    # Output format options
    parser.add_argument(
        "--format", "-f",
        choices=["json", "html", "text"],
        nargs="+",
        default=["json", "text"],
        help="Report output formats"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal console output"
    )
    
    # Development/debug options
    parser.add_argument(
        "--dry-run",
        action="store_true", 
        help="Parse tutorial but don't execute commands"
    )
    
    parser.add_argument(
        "--mock-containers",
        action="store_true",
        help="Mock container operations (for development)"
    )
    
    parser.add_argument(
        "--improve-tutorials",
        action="store_true",
        help="Generate tutorial improvement suggestions based on execution results"
    )
    
    parser.add_argument(
        "--apply-improvements",
        action="store_true",
        help="Automatically apply high-confidence tutorial improvements"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Override config with command line arguments
        if args.tutorial_files:
            config.setdefault("tutorial_test", {})["default_tutorial_files"] = args.tutorial_files
        
        if args.max_retries:
            config.setdefault("tutorial_test", {})["max_retries"] = args.max_retries
        
        if args.dry_run:
            config.setdefault("debug_config", {})["dry_run"] = True
            
        if args.mock_containers:
            config.setdefault("debug_config", {})["mock_containers"] = True
        
        # Create tutorial test agent
        agent = TutorialTestAgent(config)
        
        if not args.quiet:
            print("Starting BITS Tutorial Test Agent...")
            print(f"Configuration loaded from: {args.config or 'default'}")
            print(f"Tutorial files: {args.tutorial_files or 'all'}")
            print(f"Output directory: {args.output_dir}")
            print()
        
        # Execute tutorial tests
        result = await agent.execute(
            tutorial_files=args.tutorial_files,
            clean_environment=args.clean_env,
            stop_on_failure=args.stop_on_failure
        )
        
        # Convert result to dict for reporting
        test_run_data = result.data.get("test_run") if result.data else None
        if hasattr(test_run_data, '__dict__'):
            test_run_dict = test_run_data.__dict__
        else:
            test_run_dict = test_run_data or {}
            
        result_dict = {
            "success": result.success,
            "message": result.message,
            "test_run": test_run_dict,
            "report": result.data.get("report") if result.data else {},
            "success_rate": result.data.get("success_rate", 0) if result.data else 0
        }
        
        # Print summary to console
        if not args.quiet:
            print_summary(result_dict)
        
        # Save reports
        save_report(result_dict, args.output_dir, args.format)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        logger.info("Tutorial testing interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Tutorial testing failed: {e}")
        if args.log_level == "DEBUG":
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())