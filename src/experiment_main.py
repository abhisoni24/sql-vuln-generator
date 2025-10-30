"""Main experiment runner script.

This is the entry point for running the SQL injection vulnerability experiment.
It coordinates:
1. Loading API keys from .env
2. Running the experiment
3. Generating visualizations
4. Creating markdown reports
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Support both direct execution and module import
try:
    from .api.claude_client import ClaudeClient
    from .api.openai_client import OpenAIClient
    from .experiment_runner import ExperimentRunner
    from .utils.io import write_markdown_results
except ImportError:
    from api.claude_client import ClaudeClient
    from api.openai_client import OpenAIClient
    from experiment_runner import ExperimentRunner
    from utils.io import write_markdown_results


def setup_environment():
    """Load and validate environment variables."""
    # Search for .env file up the directory tree
    env_path = find_dotenv()
    if env_path:
        print(f"Loading environment from: {env_path}")
        load_dotenv(env_path)
    else:
        print("Warning: .env file not found. Trying to use environment variables directly.")
        load_dotenv()
    
    # Validate that API keys are set
    claude_key = os.getenv("CLAUDE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not claude_key:
        raise RuntimeError(
            "CLAUDE_API_KEY not found. Please set it in your .env file or environment variables.\n"
            "See .env.example for reference."
        )
    
    if not openai_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Please set it in your .env file or environment variables.\n"
            "See .env.example for reference."
        )
    
    print("✓ API keys loaded successfully")


def create_experiment_report(results_data, output_dir):
    """Create a comprehensive markdown report of the experiment."""
    results = results_data["results"]
    
    # Calculate statistics
    total = len(results)
    vulnerable_count = sum(1 for r in results if r["verdict"] == "VULNERABLE")
    not_vulnerable_count = sum(1 for r in results if r["verdict"] == "NOT VULNERABLE")
    error_count = sum(1 for r in results if r["verdict"] == "ERROR")
    
    vulnerable_pct = (vulnerable_count / total * 100) if total > 0 else 0
    
    # Collect CWE data
    cwe_distribution = {}
    for r in results:
        if r["cwe_id"] != "UNKNOWN":
            cwe_distribution[r["cwe_id"]] = cwe_distribution.get(r["cwe_id"], 0) + 1
    
    # Create markdown report
    markdown = "# SQL Injection Vulnerability Experiment Report\n\n"
    
    markdown += "## Executive Summary\n\n"
    markdown += (
        f"This experiment tests whether GPT-3.5-turbo generates SQL code vulnerable to "
        f"SQL injection attacks.\n\n"
        f"**Key Finding:** {vulnerable_count} out of {total} generated SQL statements "
        f"({vulnerable_pct:.1f}%) were flagged as potentially vulnerable to SQL injection.\n\n"
    )
    
    markdown += "## Methodology\n\n"
    markdown += "1. **Prompt Generation**: Claude 3.5 Sonnet generated 20 diverse natural language prompts asking for SQL code\n"
    markdown += "2. **SQL Generation**: GPT-3.5-turbo generated SQL code for each prompt\n"
    markdown += "3. **Vulnerability Analysis**: Claude 3.5 Sonnet analyzed each SQL statement for CWE vulnerabilities\n"
    markdown += "4. **Visualization**: Results were visualized for analysis\n\n"
    
    markdown += "## Results Summary\n\n"
    markdown += "| Metric | Count | Percentage |\n"
    markdown += "|--------|-------|------------|\n"
    markdown += f"| Total Samples | {total} | 100% |\n"
    markdown += f"| Vulnerable | {vulnerable_count} | {vulnerable_pct:.1f}% |\n"
    markdown += f"| Not Vulnerable | {not_vulnerable_count} | {(not_vulnerable_count/total*100):.1f}% |\n"
    markdown += f"| Errors | {error_count} | {(error_count/total*100):.1f}% |\n\n"
    
    if cwe_distribution:
        markdown += "## CWE Distribution\n\n"
        markdown += "| CWE ID | Count |\n"
        markdown += "|--------|-------|\n"
        for cwe, count in sorted(cwe_distribution.items(), key=lambda x: x[1], reverse=True):
            markdown += f"| {cwe} | {count} |\n"
        markdown += "\n"
    
    markdown += "## Detailed Results\n\n"
    for i, result in enumerate(results, 1):
        markdown += f"### Sample {i}: {result['original_prompt']}\n\n"
        markdown += "**Verdict:** " + result["verdict"] + "\n"
        if result["cwe_id"] != "UNKNOWN":
            markdown += f"**CWE:** {result['cwe_id']}\n\n"
        markdown += "**SQL Code:**\n```sql\n"
        markdown += result["sql_code"] + "\n```\n\n"
        markdown += "**Analysis:**\n\n"
        markdown += result["analysis"] + "\n\n"
        markdown += "---\n\n"
    
    # Save report
    report_path = os.path.join(output_dir, "REPORT.md")
    with open(report_path, "w") as f:
        f.write(markdown)
    
    print(f"✓ Markdown report saved: {report_path}")
    return report_path


def main(num_samples: int = 20):
    """Main entry point for the experiment."""
    print("\n" + "=" * 70)
    print("SQL INJECTION VULNERABILITY EXPERIMENT FOR GPT-3.5 GENERATED CODE")
    print("=" * 70 + "\n")
    
    # Setup
    try:
        setup_environment()
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    # Initialize clients
    print("\nInitializing API clients...")
    try:
        claude = ClaudeClient()
        openai = OpenAIClient()
        print("✓ API clients initialized")
    except RuntimeError as e:
        print(f"\n❌ Error initializing clients: {e}")
        sys.exit(1)
    
    # Create output directory
    output_dir = "experiments"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run experiment
    runner = ExperimentRunner(claude, openai)
    results_data = runner.run(n=num_samples, output_dir=output_dir)
    
    # Create markdown report
    print("\nGenerating comprehensive report...")
    create_experiment_report(results_data, output_dir)
    
    # Try to generate visualizations (optional)
    try:
        print("\nGenerating visualizations...")
        from visualizations import generate_all_visualizations
        generate_all_visualizations(results_data["json_path"], output_dir)
    except ImportError:
        print("⚠ Note: Matplotlib not installed. Skipping visualizations.")
        print("  Install with: pip install matplotlib")
    except Exception as e:
        print(f"⚠ Warning: Could not generate visualizations: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {os.path.abspath(output_dir)}/")
    print("\nGenerated files:")
    print(f"  - experiment_results.json (raw data)")
    print(f"  - REPORT.md (detailed markdown report)")
    if os.path.exists(os.path.join(output_dir, "01_vulnerability_distribution.png")):
        print(f"  - 01_vulnerability_distribution.png")
        print(f"  - 02_cwe_distribution.png")
        print(f"  - 03_summary_statistics.png")
        print(f"  - 04_sample_showcase.png")
    
    # Get and display summary statistics
    stats = runner.get_summary_statistics()
    print("\n" + "-" * 70)
    print("QUICK STATISTICS")
    print("-" * 70)
    print(f"Total Samples: {stats.get('total_samples', 0)}")
    print(f"Vulnerable: {stats.get('vulnerable', 0)} ({stats.get('vulnerable_percentage', 0):.1f}%)")
    print(f"Not Vulnerable: {stats.get('not_vulnerable', 0)}")
    print(f"Errors: {stats.get('errors', 0)}")
    if stats.get('cwe_distribution'):
        print(f"Unique CWEs Found: {len(stats['cwe_distribution'])}")
    print()


if __name__ == "__main__":
    # Allow passing number of samples as command line argument
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    main(num_samples=num_samples)
