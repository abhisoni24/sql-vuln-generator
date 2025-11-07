# Multi-Provider Quick Reference Card

## One Command Setup & Run

```bash
# Interactive setup (recommended for first time)
./quickstart_multi.sh
```

## Most Common Commands

```bash
# OpenAI GPT-3.5 (default)
python src/code_completion_main_multi.py 50

# Ollama Qwen Coder 7B (recommended local model)
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b

# Show all options
python src/code_completion_main_multi.py --help
```

## Model Comparison

| Model | Command Suffix | Pros | Cons |
|-------|---------------|------|------|
| **GPT-3.5** | *(default)* | Fast, reliable, cheap | Requires API key |
| **GPT-4** | `--model gpt-4` | Best quality | Expensive |
| **Qwen Coder 7B** | `--provider ollama --model qwen2.5-coder:7b` | Free, fast, good quality | Needs 8GB RAM |
| **Qwen Coder 14B** | `--provider ollama --model qwen2.5-coder:14b` | Free, best local | Needs 16GB RAM |
| **CodeLlama 7B** | `--provider ollama --model codellama:7b` | Free, very fast | Lower quality |
| **CodeLlama 13B** | `--provider ollama --model codellama:13b` | Free, good quality | Needs 16GB RAM |

## Quick Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start server
ollama serve

# Pull recommended model
ollama pull qwen2.5-coder:7b

# Run experiment
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b
```

## Compare Multiple Models

```bash
# Baseline with GPT-3.5
python src/code_completion_main_multi.py 50 --name gpt35-baseline

# Compare with Qwen
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b --name qwen-baseline

# Compare with CodeLlama
python src/code_completion_main_multi.py 50 --provider ollama --model codellama:7b --name codellama-baseline
```

## Output Location

```
experiments/<provider>_<model>_run_<timestamp>/
├── code_templates.json              # Test templates
├── code_completion_results.json     # Raw results
└── CODE_COMPLETION_REPORT.md        # Human-readable report
```

## Troubleshooting One-Liners

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# List available Ollama models
ollama list

# View latest experiment report
cat experiments/*/CODE_COMPLETION_REPORT.md | tail -100

# Check API keys configured
grep -E "CLAUDE_API_KEY|OPENAI_API_KEY" .env
```

## Full Documentation

- **Setup Guide**: `MULTI_PROVIDER_GUIDE.md`
- **Architecture**: `ARCHITECTURE_CHANGES.md`
- **Interactive Setup**: `./quickstart_multi.sh`
