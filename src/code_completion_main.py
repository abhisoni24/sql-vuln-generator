"""
Main entry point for the Code Completion Vulnerability Experiment.

This experiment:
1. Generates 20 incomplete Flask code templates for social media app operations
2. Uses GPT-3.5 to complete the code implementations
3. Uses Claude to analyze for SQL injection vulnerabilities
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from api.claude_client import ClaudeClient
from api.openai_client import OpenAIClient
from prompt_generator import PromptGenerator
from code_completion_runner import CodeCompletionRunner


def main(num_samples: int = 20):
    """
    Run the code completion vulnerability experiment.
    
    Args:
        num_samples: Number of code templates to generate and test
    """

    # Generate timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_experiments_dir = Path(__file__).parent.parent / "experiments"
    output_dir = base_experiments_dir / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    print("\n" + "=" * 70)
    print("SQL INJECTION VULNERABILITY EXPERIMENT - CODE COMPLETION APPROACH")
    print("=" * 70 + "\n")
    print(f"Output Directory: {output_dir}\n")

    # Load API keys
    print("Loading environment from:", env_path)
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not claude_api_key or not openai_api_key:
        print("❌ Error: API keys not found in .env file")
        print("   Please ensure CLAUDE_API_KEY and OPENAI_API_KEY are set")
        sys.exit(1)

    print("✓ API keys loaded successfully\n")

    # Initialize API clients
    print("Initializing API clients...")
    claude_client = ClaudeClient(api_key=claude_api_key)
    openai_client = OpenAIClient(api_key=openai_api_key)
    print("✓ API clients initialized\n")

    # Step 1: Generate code templates
    print("=" * 70)
    print("STEP 1: GENERATING CODE TEMPLATES")
    print("=" * 70 + "\n")

    print(f"Generating {num_samples} incomplete Flask code templates...")
    templates = PromptGenerator.generate_prompts(claude_client, num_prompts=num_samples)

    # Save templates
    templates_file = PromptGenerator.save_templates_to_file(templates, str(output_dir))
    print(f"✓ Generated {len(templates)} code templates")
    print(f"✓ Templates saved to: {templates_file}\n")

    # Step 2: Run code completion and vulnerability analysis
    print("=" * 70)
    print("STEP 2: CODE COMPLETION AND VULNERABILITY ANALYSIS")
    print("=" * 70)

    runner = CodeCompletionRunner(openai_client, claude_client)
    summary = runner.run_experiment(templates, str(output_dir))

    # Step 3: Export detailed report
    print("\n" + "=" * 70)
    print("STEP 3: GENERATING REPORT")
    print("=" * 70 + "\n")

    report_path = runner.export_results_to_markdown(str(output_dir))
    print(f"✓ Detailed report saved to: {report_path}\n")

    # Display summary
    print("=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70 + "\n")

    print("QUICK STATISTICS")
    print("-" * 70)
    print(f"Total Scenarios: {summary['total_samples']}")
    print(f"Vulnerable Code: {summary['vulnerable']} ({summary['vulnerability_rate']})")
    print(f"Safe Code: {summary['safe']}")
    print(f"Errors: {summary['errors']}\n")

    if summary["cwe_distribution"]:
        print("CWE Types Found:")
        for cwe, count in summary["cwe_distribution"].items():
            print(f"  - {cwe}: {count}")
        print()

    if summary["severity_distribution"]:
        print("Severity Distribution:")
        for severity, count in summary["severity_distribution"].items():
            print(f"  - {severity}: {count}")

    print("\n" + "=" * 70)
    print(f"Results saved to: {output_dir}")
    print("=" * 70 + "\n")

    return summary


if __name__ == "__main__":
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    main(num_samples=num_samples)
