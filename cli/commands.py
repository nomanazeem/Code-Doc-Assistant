# cli/commands.py
import click
import os
from pathlib import Path
from ..agents.parser_agent import ParserAgent
from ..core.vector_store import CodeVectorStore
from ..core.rag_pipeline import RAGPipeline
from ..agents.doc_generator_agent import DocumentationGeneratorAgent
from ..agents.consistency_agent import ConsistencyAgent

@click.group()
def cli():
    """Code Documentation Assistant - Generate and improve code documentation."""
    pass

@cli.command()
@click.argument('codebase_path')
@click.option('--output-dir', default='./doc_output', help='Output directory for generated documentation')
@click.option('--openai-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
def generate(codebase_path: str, output_dir: str, openai_key: str):
    """Generate documentation for a codebase."""
    click.echo("Starting documentation generation...")

    # Initialize agents
    parser_agent = ParserAgent()
    vector_store = CodeVectorStore()

    # Parse codebase
    click.echo("Parsing codebase...")
    parsed_data = parser_agent.parse_codebase(codebase_path)

    # Index codebase
    click.echo("Indexing codebase...")
    vector_store.index_codebase(parsed_data)

    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(vector_store, openai_key)
    doc_generator = DocumentationGeneratorAgent(rag_pipeline)
    consistency_agent = ConsistencyAgent()

    # Generate documentation
    click.echo("Generating documentation...")
    generated_docs = doc_generator.generate_docstrings(parsed_data)

    # Analyze consistency
    click.echo("Analyzing consistency...")
    consistency_report = consistency_agent.analyze_consistency(parsed_data, generated_docs)

    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save generated documentation
    with open(output_path / 'generated_docs.json', 'w') as f:
        import json
        json.dump(generated_docs, f, indent=2)

    # Save consistency report
    with open(output_path / 'consistency_report.json', 'w') as f:
        json.dump(consistency_report, f, indent=2)

    # Print summary
    _print_summary(generated_docs, consistency_report)

@cli.command()
@click.argument('codebase_path')
def analyze(codebase_path: str):
    """Analyze documentation quality of a codebase."""
    click.echo("Analyzing documentation quality...")

    parser_agent = ParserAgent()
    consistency_agent = ConsistencyAgent()

    # Parse codebase
    parsed_data = parser_agent.parse_codebase(codebase_path)

    # Analyze consistency
    analysis = consistency_agent.analyze_consistency(parsed_data, {})

    # Print analysis results
    click.echo("\n=== Documentation Analysis Report ===")

    if analysis['style_issues']:
        click.echo("\nStyle Issues:")
        for issue in analysis['style_issues']:
            click.echo(f"  - {issue}")

    if analysis['coverage_issues']:
        click.echo("\nCoverage Issues:")
        for issue in analysis['coverage_issues']:
            click.echo(f"  - {issue}")

    if analysis['recommendations']:
        click.echo("\nRecommendations:")
        for rec in analysis['recommendations']:
            click.echo(f"  - {rec}")

def _print_summary(generated_docs: dict, consistency_report: dict):
    """Print a summary of the documentation generation."""
    total_generated = (len(generated_docs.get('functions', [])) +
                      len(generated_docs.get('classes', [])))

    click.echo(f"\n=== Documentation Generation Summary ===")
    click.echo(f"Generated documentation for {total_generated} elements")
    click.echo(f"Functions: {len(generated_docs.get('functions', []))}")
    click.echo(f"Classes: {len(generated_docs.get('classes', []))}")

    if consistency_report.get('coverage_issues'):
        click.echo("\nCoverage Report:")
        for issue in consistency_report['coverage_issues']:
            click.echo(f"  - {issue}")