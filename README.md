# LLM Code Generation & Vulnerability Analysis

A simplified framework for testing LLM performance in generating secure SQL code and analyzing vulnerabilities.

## Quick Start

Run experiments with different LLM combinations:

```bash
# Claude generates code, Gemini analyzes vulnerabilities
python main.py --generator claude --analyzer gemini

# Gemini generates code, Claude analyzes vulnerabilities
python main.py --generator gemini --analyzer claude

# OpenAI generates code, Claude analyzes vulnerabilities
python main.py --generator openai --analyzer claude
```

## Available Options

- **Generators**: `claude`, `gemini`, `openai`
- **Analyzers**: `claude`, `gemini`, `openai`
- **Scenarios**: `vulnerable_12` (12 known vulnerable SQL injection scenarios)

## Examples

```bash
# Basic experiment
python main.py -g claude -a gemini

# Specify models
python main.py -g claude -m claude-3-5-haiku-20241022 -a gemini -n gemini-2.5-pro

# Custom experiment name
python main.py -g gemini -a claude --name my_experiment

# Different scenario set
python main.py -g claude -a gemini -s vulnerable_12
```

## Output

Results are saved to `experiments/` with:
- `results.json`: Complete experiment data
- `REPORT.md`: Human-readable summary

## Environment Setup

Set your API keys in `.env`:

```bash
CLAUDE_API_KEY=your_claude_key
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
```

## Architecture

- **LLM Factory**: Unified interface for all LLM providers
- **Simple Experiment Runner**: Handles code generation and analysis
- **Configuration-Driven**: Easy to add new providers and scenarios

## Adding New Providers

1. Create a new client in `src/api/` inheriting from `BaseLLMClient`
2. Add to `LLMFactory.PROVIDERS`
3. Implement required methods: `get_sql_code()`, `send_prompt_with_system()`, `get_model_name()`, `get_provider_name()`