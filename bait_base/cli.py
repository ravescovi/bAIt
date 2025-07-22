"""
bAIt CLI Commands

This module provides the command-line interface for bAIt using Typer.
It implements all the CLI commands defined in pyproject.toml.
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .analyzers import AnalysisResult, DeploymentAnalyzer
from .config import find_deployment_config, load_deployment_config
from .query_system import QueryProcessor

# Initialize console and typer app
console = Console()
app = typer.Typer(
    name="bait",
    help="bAIt (Bluesky AI Tools) - Analysis and Intelligence Framework",
    add_completion=False,
)


def print_analysis_result(result: AnalysisResult, verbose: bool = False) -> None:
    """Print analysis result in a formatted way."""
    # Status indicator
    status_color = {
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }.get(result.status, "white")

    # Create header
    header = Panel(
        f"[bold]{result.analyzer_name.upper()} ANALYSIS[/bold]\n"
        f"Status: [{status_color}]{result.status.upper()}[/{status_color}]\n"
        f"Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Summary: {result.summary}",
        title="Analysis Results",
        border_style=status_color
    )
    console.print(header)

    # Print issues if any
    if result.issues:
        console.print("\n[bold red]Issues Found:[/bold red]")
        for issue in result.issues:
            severity_color = {
                "error": "red",
                "warning": "yellow",
                "info": "blue"
            }.get(issue.get("severity", "info"), "white")

            location = f" ({issue['location']})" if issue.get("location") else ""
            console.print(f"  [{severity_color}]{issue['severity'].upper()}[/{severity_color}]: {issue['message']}{location}")

    # Print recommendations if any
    if result.recommendations:
        console.print("\n[bold blue]Recommendations:[/bold blue]")
        for rec in result.recommendations:
            console.print(f"  • {rec}")

    # Print details if verbose
    if verbose and result.details:
        console.print("\n[bold]Details:[/bold]")
        # Format details as JSON
        details_json = json.dumps(result.details, indent=2)
        syntax = Syntax(details_json, "json", theme="monokai", line_numbers=True)
        console.print(syntax)


@app.command()
def analyze(
    deployment_name: str = typer.Argument(..., help="Name of the deployment to analyze"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    output_format: str = typer.Option("console", "--format", "-f", help="Output format (console, json, html)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    save_results: bool = typer.Option(False, "--save", "-s", help="Save results to file")
) -> None:
    """
    Analyze a deployment configuration.

    This command performs comprehensive analysis of a deployment including
    IOCs, Bluesky configurations, MEDM screens, and network topology.
    """
    try:
        # Find or load configuration
        if config_path:
            config_file = config_path
        else:
            config_file = find_deployment_config(deployment_name)
            if not config_file:
                console.print(f"[red]Error: Could not find configuration for deployment '{deployment_name}'[/red]")
                console.print("Try specifying the config path with --config option")
                raise typer.Exit(1)

        console.print(f"[green]Analyzing deployment: {deployment_name}[/green]")
        console.print(f"[dim]Configuration: {config_file}[/dim]")

        # Load configuration
        config = load_deployment_config(config_file)

        # Create analyzer and run analysis
        analyzer = DeploymentAnalyzer()
        result = analyzer.analyze(config)

        # Output results
        if output_format == "console":
            print_analysis_result(result, verbose)
        elif output_format == "json":
            console.print(json.dumps(result.to_dict(), indent=2))
        elif output_format == "html":
            console.print("[yellow]HTML output not yet implemented[/yellow]")

        # Save results if requested
        if save_results:
            output_file = Path(f"{deployment_name}_analysis.json")
            with open(output_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            console.print(f"[green]Results saved to: {output_file}[/green]")

        # Set exit code based on results
        if result.has_errors():
            raise typer.Exit(1)
        elif result.has_warnings():
            raise typer.Exit(2)
        else:
            raise typer.Exit(0)

    except Exception as e:
        console.print(f"[red]Error during analysis: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def query(
    deployment_name: str = typer.Argument(..., help="Name of the deployment to query"),
    question: str = typer.Argument(..., help="Question to ask about the deployment"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
) -> None:
    """
    Query a deployment using natural language.

    Ask questions about the deployment configuration and get intelligent answers.
    """
    try:
        # Find or load configuration
        if config_path:
            config_file = config_path
        else:
            config_file = find_deployment_config(deployment_name)
            if not config_file:
                console.print(f"[red]Error: Could not find configuration for deployment '{deployment_name}'[/red]")
                console.print("Try specifying the config path with --config option")
                raise typer.Exit(1)

        console.print(f"[blue]Querying deployment: {deployment_name}[/blue]")
        console.print(f"[dim]Question: {question}[/dim]")

        # Load configuration
        config = load_deployment_config(config_file)

        # Create query processor and process query
        query_processor = QueryProcessor()
        result = query_processor.query(config, question)

        # Display result
        confidence_color = "green" if result.confidence > 0.7 else "yellow" if result.confidence > 0.3 else "red"

        console.print(f"\n[bold]Answer:[/bold] {result.answer}")
        console.print(f"[{confidence_color}]Confidence: {result.confidence:.1%}[/{confidence_color}]")
        console.print(f"[dim]Source: {result.source}[/dim]")

        # Show related data if verbose
        if verbose and result.related_data:
            console.print("\n[bold]Related Data:[/bold]")
            for data in result.related_data:
                console.print(f"  • {data.get('type', 'unknown')}: {data.get('name', 'N/A')}")

        # Show details if verbose
        if verbose and result.details:
            console.print("\n[bold]Details:[/bold]")
            details_json = json.dumps(result.details, indent=2)
            syntax = Syntax(details_json, "json", theme="monokai", line_numbers=True)
            console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error during query: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def report(
    deployment_name: str = typer.Argument(..., help="Name of the deployment"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    output_path: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("html", "--format", "-f", help="Report format (html, pdf, md)")
) -> None:
    """
    Generate a comprehensive report for a deployment.

    Creates detailed reports with analysis results, visualizations, and recommendations.
    """
    console.print(f"[blue]Generating report for: {deployment_name}[/blue]")
    console.print("[yellow]Report generation not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 4[/dim]")


@app.command()
def visualize(
    deployment_name: str = typer.Argument(..., help="Name of the deployment"),
    viz_type: str = typer.Option("network", "--type", "-t", help="Visualization type (network, dependencies, overview)"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    output_path: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("svg", "--format", "-f", help="Output format (svg, png, pdf, html)")
) -> None:
    """
    Generate visualizations for a deployment.

    Create network diagrams, dependency graphs, and system overviews.
    """
    console.print(f"[blue]Generating {viz_type} visualization for: {deployment_name}[/blue]")
    console.print("[yellow]Visualization generation not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 3[/dim]")


@app.command()
def create_deployment(
    deployment_name: str = typer.Argument(..., help="Name of the new deployment"),
    beamline: str | None = typer.Option(None, "--beamline", "-b", help="Beamline identifier"),
    template: str = typer.Option("default", "--template", "-t", help="Template to use"),
    output_path: Path | None = typer.Option(None, "--output", "-o", help="Output directory")
) -> None:
    """
    Create a new deployment configuration.

    Creates a new deployment configuration directory with template files.
    """
    console.print(f"[blue]Creating new deployment: {deployment_name}[/blue]")
    console.print("[yellow]Deployment creation not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 2[/dim]")


@app.command()
def update_deployment(
    deployment_name: str = typer.Argument(..., help="Name of the deployment to update"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update even if there are conflicts")
) -> None:
    """
    Update deployment data from repositories.

    Pulls latest data from configured repositories and updates local cache.
    """
    console.print(f"[blue]Updating deployment: {deployment_name}[/blue]")
    console.print("[yellow]Deployment update not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 2[/dim]")


@app.command()
def sync(
    deployment_name: str = typer.Argument(..., help="Name of the deployment to sync"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be synced without doing it")
) -> None:
    """
    Sync deployment configuration with remote sources.

    Synchronizes local deployment data with remote repositories.
    """
    console.print(f"[blue]Syncing deployment: {deployment_name}[/blue]")
    console.print("[yellow]Deployment sync not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 2[/dim]")


@app.command()
def build_knowledge(
    deployment_name: str = typer.Argument(..., help="Name of the deployment"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    rebuild: bool = typer.Option(False, "--rebuild", "-r", help="Rebuild knowledge base from scratch")
) -> None:
    """
    Build knowledge base for a deployment.

    Creates embeddings and knowledge base for intelligent querying.
    """
    console.print(f"[blue]Building knowledge base for: {deployment_name}[/blue]")
    console.print("[yellow]Knowledge base building not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 3[/dim]")


@app.command()
def update_embeddings(
    deployment_name: str = typer.Argument(..., help="Name of the deployment"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    incremental: bool = typer.Option(True, "--incremental", "-i", help="Only update changed files")
) -> None:
    """
    Update embeddings for a deployment.

    Updates the embedding vectors for improved querying performance.
    """
    console.print(f"[blue]Updating embeddings for: {deployment_name}[/blue]")
    console.print("[yellow]Embedding updates not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 3[/dim]")


@app.command()
def test_retrieval(
    deployment_name: str = typer.Argument(..., help="Name of the deployment"),
    query: str = typer.Argument(..., help="Test query"),
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Path to deployment configuration"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of results to return")
) -> None:
    """
    Test retrieval system with a query.

    Tests the knowledge base retrieval system with a sample query.
    """
    console.print(f"[blue]Testing retrieval for: {deployment_name}[/blue]")
    console.print(f"[dim]Query: {query}[/dim]")
    console.print("[yellow]Retrieval testing not yet implemented[/yellow]")
    console.print("[dim]This feature will be available in Phase 3[/dim]")


@app.command()
def list_deployments(
    base_path: Path | None = typer.Option(None, "--path", "-p", help="Base path to search for deployments")
) -> None:
    """
    List available deployments.

    Shows all available deployment configurations.
    """
    console.print("[blue]Available deployments:[/blue]")

    # Default path
    if not base_path:
        base_path = Path("bait_deployments")

    if not base_path.exists():
        console.print(f"[red]Deployment directory not found: {base_path}[/red]")
        return

    # Find deployments
    deployments = []
    for item in base_path.iterdir():
        if item.is_dir() and (item / "config.json").exists():
            deployments.append(item.name)

    if not deployments:
        console.print("[yellow]No deployments found[/yellow]")
        return

    # Create table
    table = Table(title="Available Deployments")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="dim")
    table.add_column("Status", style="green")

    for deployment in sorted(deployments):
        deployment_path = base_path / deployment
        status = "✓ Ready" if (deployment_path / "config.json").exists() else "⚠ Incomplete"
        table.add_row(deployment, str(deployment_path), status)

    console.print(table)


@app.command()
def version() -> None:
    """Show bAIt version information."""
    try:
        from . import __version__
        console.print(f"[bold]bAIt[/bold] version [green]{__version__}[/green]")
    except ImportError:
        console.print("[red]Version information not available[/red]")


if __name__ == "__main__":
    app()
