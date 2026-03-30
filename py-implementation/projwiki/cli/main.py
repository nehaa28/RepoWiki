"""
Main CLI interface for ProjWiki
"""

import click
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..parser.analyzer import CodebaseAnalyzer
from ..ai.summarizer import AISummarizer
from ..diagram.generator import DiagramGenerator
from ..generator.site_builder import SiteBuilder

console = Console()


@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--depth', default=5, help='Maximum depth for directory traversal')
@click.option('--diagram-only', is_flag=True, help='Generate only architecture diagrams')
@click.option('--offline', is_flag=True, help='Skip AI summarization (offline mode)')
@click.option('--output', '-o', default='./output', help='Output directory')
def main(project_path, depth, diagram_only, offline, output):
    """
    Generate interactive documentation for a codebase.

    Usage:
        projwiki ./my-project
        projwiki ./my-project --depth 3 --output ./docs
    """
    console.print("[bold blue]🚀 ProjWiki - Codebase Documentation Generator[/bold blue]\n")

    project_path = Path(project_path).resolve()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_path = Path(output).resolve() / timestamp

    console.print(f"📂 Analyzing: [cyan]{project_path}[/cyan]")
    console.print(f"📝 Output to: [cyan]{output_path}[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Step 1: Parse codebase
        task1 = progress.add_task("Parsing codebase...", total=None)
        analyzer = CodebaseAnalyzer(project_path, max_depth=depth)
        analysis_result = analyzer.analyze()
        progress.update(task1, completed=True)
        console.print(f"✓ Found {analysis_result['file_count']} files\n")

        # Step 2: Generate diagrams
        task2 = progress.add_task("Generating architecture diagrams...", total=None)
        diagram_gen = DiagramGenerator(analysis_result)
        diagrams = diagram_gen.generate_all()
        progress.update(task2, completed=True)
        console.print(f"✓ Generated {len(diagrams)} diagrams\n")

        if diagram_only:
            console.print("[green]✓ Diagram-only mode complete![/green]")
            return

        # Step 3: AI Summarization (if not offline)
        summaries = None
        if not offline:
            task3 = progress.add_task("Generating AI summaries...", total=None)
            summarizer = AISummarizer()
            summaries = summarizer.summarize_codebase(analysis_result)
            progress.update(task3, completed=True)
            console.print(f"✓ Generated summaries for {len(summaries)} files\n")

        # Step 4: Build static site
        task4 = progress.add_task("Building static site...", total=None)
        builder = SiteBuilder(output_path)
        builder.build(analysis_result, diagrams, summaries)
        progress.update(task4, completed=True)

    console.print("\n[bold green]✨ Documentation generated successfully![/bold green]")
    console.print(f"\n📖 HTML : [cyan]{output_path / 'index.html'}[/cyan]")
    console.print(f"📄 README: [cyan]{output_path / 'README.md'}[/cyan]")


if __name__ == "__main__":
    main()
