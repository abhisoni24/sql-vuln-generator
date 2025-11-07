"""
Main entry point for the Code Completion Vulnerability Experiment with Multi-Provider Support.

This experiment:
1. Generates incomplete Flask code templates for social media app operations
2. Uses various LLM providers (OpenAI GPT, Ollama Qwen, etc.) to complete the code
3. Uses Claude to analyze for SQL injection vulnerabilities

Supports multiple code generation providers:
- OpenAI (GPT-3.5, GPT-4)
- Ollama (Qwen, Llama, CodeLlama, DeepSeek, Mistral, etc.)
- Additional providers can be added by implementing BaseLLMClient
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from api.claude_client import ClaudeClient
from api.openai_client import OpenAIClient
from api.ollama_client import OllamaClient, OllamaModels
from prompt_generator import PromptGenerator
from code_completion_runner import CodeCompletionRunner


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SQL Injection Vulnerability Experiment with Multi-Provider Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with OpenAI GPT-3.5 (default)
  python code_completion_main.py 50
  
  # Run with Ollama Qwen Coder
  python code_completion_main.py 50 --provider ollama --model qwen2.5-coder:7b
  
  # Run with Ollama Llama 3.1
  python code_completion_main.py 30 --provider ollama --model llama3.1:8b
  
  # Run with custom experiment name
  python code_completion_main.py 50 --provider ollama --model qwen2.5-coder:7b --name qwen-coder-test

Available Ollama Models:
  - qwen2.5-coder:7b (recommended for code)
  - qwen2.5-coder:14b
  - codellama:7b
  - codellama:13b
  - deepseek-coder:6.7b
  - llama3.1:8b
  - mistral:7b
"""
    )
    
    parser.add_argument(
        "num_samples",
        type=int,
        nargs="?",
        default=20,
        help="Number of code templates to generate and test (default: 20)"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "ollama"],
        default="openai",
        help="LLM provider to use for code generation (default: openai)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Specific model to use (e.g., 'gpt-3.5-turbo' for OpenAI, 'qwen2.5-coder:7b' for Ollama)"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        help="Custom name for the experiment run (will be appended to timestamp)"
    )
    
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    
    return parser.parse_args()


def initialize_code_generator(args):
    """
    Initialize the appropriate code generation client based on provider.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Instance of a BaseLLMClient implementation
    """
    if args.provider == "openai":
        # OpenAI GPT
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Error: OPENAI_API_KEY not found in .env file")
            sys.exit(1)
        
        model = args.model or "gpt-3.5-turbo"
        print(f"✓ Initializing OpenAI client (model: {model})")
        return OpenAIClient(api_key=api_key, model=model)
    
    elif args.provider == "ollama":
        # Ollama (local models)
        model = args.model or OllamaModels.QWEN_CODER_7B
        
        # Get recommended context window
        context_window = OllamaModels.get_recommended_context_window(model)
        
        print(f"✓ Initializing Ollama client (model: {model}, context: {context_window})")
        print(f"  Note: Ensure Ollama server is running at {args.ollama_url}")
        
        try:
            return OllamaClient(
                model=model,
                base_url=args.ollama_url,
                context_window=context_window
            )
        except Exception as e:
            print(f"❌ Error: Failed to initialize Ollama client: {e}")
            print("   Make sure Ollama server is running (run 'ollama serve')")
            print(f"   And the model '{model}' is available (run 'ollama pull {model}')")
            sys.exit(1)
    
    else:
        print(f"❌ Error: Unsupported provider: {args.provider}")
        sys.exit(1)


def main():
    """
    Run the code completion vulnerability experiment with the selected provider.
    """
    args = parse_arguments()
    
    # Generate timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_experiments_dir = Path(__file__).parent.parent / "experiments"
    
    # Create experiment name with provider info
    if args.name:
        exp_name = f"{args.name}_run_{timestamp}"
    else:
        provider_model = args.model or (
            "gpt-3.5-turbo" if args.provider == "openai" 
            else OllamaModels.QWEN_CODER_7B
        )
        # Sanitize model name for directory
        model_safe = provider_model.replace(":", "-").replace("/", "-")
        exp_name = f"{args.provider}_{model_safe}_run_{timestamp}"
    
    output_dir = base_experiments_dir / exp_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    print("\n" + "=" * 70)
    print("SQL INJECTION VULNERABILITY EXPERIMENT - MULTI-PROVIDER")
    print("=" * 70 + "\n")
    print(f"Provider: {args.provider.upper()}")
    print(f"Output Directory: {output_dir}\n")

    # Load Claude API key (always needed for analysis)
    print("Loading environment from:", env_path)
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    
    if not claude_api_key:
        print("❌ Error: CLAUDE_API_KEY not found in .env file")
        print("   Claude is required for vulnerability analysis")
        sys.exit(1)

    print("✓ Claude API key loaded\n")

    # Initialize clients
    print("Initializing API clients...")
    claude_client = ClaudeClient(api_key=claude_api_key)
    code_generator = initialize_code_generator(args)
    print("✓ All clients initialized\n")

    # Step 1: Generate code templates
    print("=" * 70)
    print("STEP 1: GENERATING CODE TEMPLATES")
    print("=" * 70 + "\n")

    print(f"Generating {args.num_samples} incomplete Flask code templates...")
    templates = PromptGenerator.generate_prompts(claude_client, num_prompts=args.num_samples)

    # Save templates
    templates_file = PromptGenerator.save_templates_to_file(templates, str(output_dir))
    print(f"✓ Generated {len(templates)} code templates")
    print(f"✓ Templates saved to: {templates_file}\n")

    # Step 2: Run code completion and vulnerability analysis
    print("=" * 70)
    print("STEP 2: CODE COMPLETION AND VULNERABILITY ANALYSIS")
    print("=" * 70)

    # Create runner with the selected code generator
    runner = CodeCompletionRunner(
        code_generator_client=code_generator,
        claude_client=claude_client,
        sql_reference_path="checks/sql/sql_owasp_reference.md"
    )
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
    print(f"Code Generator: {code_generator.get_provider_name()} ({code_generator.get_model_name()})")
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
    main()
