"""
Example usage of ProjWiki

This demonstrates how to use ProjWiki programmatically
"""

from pathlib import Path
from projwiki.parser.analyzer import CodebaseAnalyzer
from projwiki.diagram.generator import DiagramGenerator
from projwiki.generator.site_builder import SiteBuilder

# You can also use AI summarization if you have an API key
# from projwiki.ai.summarizer import AISummarizer


def generate_docs_for_project(project_path: str, output_path: str = "./output"):
    """
    Generate documentation for a project

    Args:
        project_path: Path to the codebase
        output_path: Where to save the documentation
    """
    print("📚 Generating documentation...")

    # Step 1: Analyze codebase
    print("  🔍 Analyzing codebase...")
    analyzer = CodebaseAnalyzer(Path(project_path), max_depth=5)
    analysis = analyzer.analyze()
    print(f"     Found {analysis['file_count']} files")

    # Step 2: Generate diagrams
    print("  📊 Generating diagrams...")
    diagram_gen = DiagramGenerator(analysis)
    diagrams = diagram_gen.generate_all()
    print(f"     Created {len(diagrams)} diagrams")

    # Step 3: (Optional) Generate AI summaries
    # Uncomment if you have SAP AI Core credentials configured
    # print("  🤖 Generating AI summaries...")
    # summarizer = AISummarizer()
    # summaries = summarizer.summarize_codebase(analysis)
    summaries = None

    # Step 4: Build site
    print("  🏗️  Building static site...")
    builder = SiteBuilder(Path(output_path))
    builder.build(analysis, diagrams, summaries)

    print(f"\n✅ Done! Open {output_path}/index.html to view.")


if __name__ == "__main__":
    # Example: Generate docs for this project itself
    generate_docs_for_project(".", "./output")

    # Example: Generate docs for another project
    # generate_docs_for_project("/path/to/other/project", "./other_output")
