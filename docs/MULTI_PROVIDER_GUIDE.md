# Multi-Provider LLM Support Guide

This guide explains how to run the SQL injection vulnerability experiment with different LLM providers for code generation.

## Overview

The experiment now supports multiple LLM providers for code generation:
- **OpenAI** (GPT-3.5, GPT-4)
- **Ollama** (Qwen, Llama, CodeLlama, DeepSeek, Mistral, etc.)
- Extensible architecture for adding more providers

**Note:** Claude is always used for vulnerability analysis (with cached SQL reference for efficiency).

## Architecture

### Components

1. **BaseLLMClient** (`src/api/base_llm_client.py`)
   - Abstract base class defining the interface for all LLM providers
   - Ensures consistent API across different providers

2. **OpenAIClient** (`src/api/openai_client.py`)
   - OpenAI GPT models (GPT-3.5-turbo, GPT-4, etc.)
   - Requires `OPENAI_API_KEY` in `.env`

3. **OllamaClient** (`src/api/ollama_client.py`)
   - Local LLM models via Ollama
   - Supports Qwen, Llama, CodeLlama, DeepSeek, Mistral, etc.
   - No API key required (runs locally)

4. **CodeCompletionRunner** (`src/code_completion_runner.py`)
   - Provider-agnostic experiment orchestrator
   - Accepts any BaseLLMClient implementation
   - Tracks provider/model metadata in results

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `openai` - OpenAI API client
- `anthropic` - Claude API client
- `langchain-ollama` - Ollama integration
- `langchain-core` - LangChain core utilities

### 2. OpenAI Setup (Optional)

If using OpenAI models:

```bash
# Add to .env file
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Ollama Setup (Optional)

If using Ollama for local models:

#### Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Or download from:** https://ollama.ai/download

#### Start Ollama Server

```bash
ollama serve
```

#### Pull Models

```bash
# Recommended: Qwen 2.5 Coder (excellent for code generation)
ollama pull qwen2.5-coder:7b

# Alternative models
ollama pull qwen2.5-coder:14b    # Larger Qwen coder
ollama pull codellama:7b         # Meta's CodeLlama
ollama pull llama3.1:8b          # General purpose Llama
ollama pull deepseek-coder:6.7b  # DeepSeek coder
ollama pull mistral:7b           # Mistral
```

**Model Size Recommendations:**
- 7B models: Good for most systems (8GB+ RAM)
- 13-14B models: Better quality, needs 16GB+ RAM
- 32B+ models: Best quality, needs 32GB+ RAM

## Usage

### Basic Usage

#### OpenAI (Default)
```bash
# Run with GPT-3.5 Turbo (default)
python src/code_completion_main_multi.py 50

# Run with GPT-4
python src/code_completion_main_multi.py 50 --model gpt-4
```

#### Ollama (Local Models)
```bash
# Run with Qwen Coder 7B (recommended for code)
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b

# Run with CodeLlama
python src/code_completion_main_multi.py 50 --provider ollama --model codellama:13b

# Run with Llama 3.1
python src/code_completion_main_multi.py 30 --provider ollama --model llama3.1:8b

# Run with DeepSeek Coder
python src/code_completion_main_multi.py 50 --provider ollama --model deepseek-coder:6.7b
```

### Advanced Options

```bash
# Custom experiment name
python src/code_completion_main_multi.py 50 \
  --provider ollama \
  --model qwen2.5-coder:7b \
  --name qwen-baseline-test

# Custom Ollama server URL
python src/code_completion_main_multi.py 50 \
  --provider ollama \
  --model qwen2.5-coder:7b \
  --ollama-url http://192.168.1.100:11434

# Different number of test scenarios
python src/code_completion_main_multi.py 100 --provider ollama --model qwen2.5-coder:14b
```

### Command Line Help

```bash
python src/code_completion_main_multi.py --help
```

## Comparing Providers

### Running Comparative Experiments

```bash
# Test 1: OpenAI GPT-3.5
python src/code_completion_main_multi.py 50 --name gpt35-baseline

# Test 2: Qwen Coder 7B
python src/code_completion_main_multi.py 50 \
  --provider ollama \
  --model qwen2.5-coder:7b \
  --name qwen-7b-baseline

# Test 3: CodeLlama 13B
python src/code_completion_main_multi.py 50 \
  --provider ollama \
  --model codellama:13b \
  --name codellama-13b-baseline
```

Results will be saved in separate directories:
```
experiments/
├── gpt35-baseline_run_20251105_120000/
├── qwen-7b-baseline_run_20251105_123000/
└── codellama-13b-baseline_run_20251105_130000/
```

### Analyzing Results

Each experiment generates:
1. `code_completion_results.json` - Raw results with all data
2. `CODE_COMPLETION_REPORT.md` - Human-readable report
3. `code_templates.json` - Original templates used

Compare the reports to see:
- Vulnerability rates by provider
- Types of vulnerabilities generated
- Code quality differences

## Output Structure

```
experiments/
└── <provider>_<model>_run_<timestamp>/
    ├── code_templates.json              # Generated templates
    ├── code_completion_results.json     # Full results
    └── CODE_COMPLETION_REPORT.md        # Detailed report
```

### Report Contents

The markdown report includes:

1. **Experiment Configuration**
   - Code generator provider and model
   - Vulnerability analyzer (always Claude)
   
2. **Executive Summary**
   - Total scenarios tested
   - Vulnerability rate
   - CWE distribution
   - Severity distribution
   
3. **Detailed Results**
   - Each scenario with template, generated code, and analysis
   - Matched vulnerability check IDs (SQLI-001, SQLI-002, etc.)
   - Remediation recommendations

## Recommended Model Combinations

### For Code Generation Quality

| Use Case | Provider | Model | Why |
|----------|----------|-------|-----|
| Best Accuracy | OpenAI | gpt-4 | Highest quality code |
| Cost-Effective Cloud | OpenAI | gpt-3.5-turbo | Good quality, lower cost |
| Local - Best Code | Ollama | qwen2.5-coder:14b | Specialized for coding |
| Local - Balanced | Ollama | qwen2.5-coder:7b | Good quality, runs on most systems |
| Local - Fast | Ollama | codellama:7b | Quick, decent quality |
| Local - Instruction Following | Ollama | llama3.1:8b | Strong general model |

### Performance Comparison (Approximate)

| Model | Size | Speed | Quality | RAM Required |
|-------|------|-------|---------|--------------|
| gpt-3.5-turbo | - | Very Fast | High | - (API) |
| gpt-4 | - | Medium | Very High | - (API) |
| qwen2.5-coder:7b | 4.7GB | Fast | High | 8GB+ |
| qwen2.5-coder:14b | 8.9GB | Medium | Very High | 16GB+ |
| codellama:7b | 3.8GB | Very Fast | Medium-High | 8GB+ |
| codellama:13b | 7.4GB | Medium | High | 16GB+ |
| llama3.1:8b | 4.7GB | Fast | High | 8GB+ |
| deepseek-coder:6.7b | 3.8GB | Fast | Medium-High | 8GB+ |

## Adding New Providers

To add support for a new LLM provider:

1. Create a new client class inheriting from `BaseLLMClient`:

```python
from src.api.base_llm_client import BaseLLMClient

class CustomProviderClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        # Initialize your client
    
    def get_sql_code(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        # Implement code generation logic
        pass
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "CustomProvider"
```

2. Add initialization logic to `code_completion_main_multi.py`:

```python
elif args.provider == "custom":
    api_key = os.getenv("CUSTOM_API_KEY")
    return CustomProviderClient(api_key=api_key, model=args.model)
```

3. Update the argument parser to include your provider.

## Troubleshooting

### Ollama Issues

**Error: "Failed to initialize Ollama client"**
- Ensure Ollama server is running: `ollama serve`
- Check if model is available: `ollama list`
- Pull the model if missing: `ollama pull <model-name>`

**Error: "Connection refused"**
- Verify Ollama is running on the correct port (default: 11434)
- Use `--ollama-url` to specify custom URL if needed

**Slow generation**
- Larger models (13B+) require more RAM and are slower
- Try smaller models (7B) for faster results
- Ensure no other heavy processes are running

### OpenAI Issues

**Error: "OpenAI API key not found"**
- Add `OPENAI_API_KEY` to your `.env` file
- Verify the key is valid

**Rate limiting**
- Experiment includes 1-second delays between requests
- For large experiments, consider upgrading API tier

### General Issues

**Out of memory**
- Use smaller models (7B instead of 13B+)
- Close other applications
- Reduce `num_samples` parameter

**Import errors**
- Run `pip install -r requirements.txt`
- Ensure virtual environment is activated

## Example Workflow

Complete workflow for comparing providers:

```bash
# 1. Setup
pip install -r requirements.txt
ollama serve &  # Start Ollama in background

# 2. Pull models
ollama pull qwen2.5-coder:7b
ollama pull codellama:7b

# 3. Run experiments
python src/code_completion_main_multi.py 50 --name gpt35-test
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b --name qwen-test
python src/code_completion_main_multi.py 50 --provider ollama --model codellama:7b --name codellama-test

# 4. Compare results
# Review the CODE_COMPLETION_REPORT.md files in each experiment directory
```

## Tips for Best Results

1. **Use Coding Models for Code Tasks**
   - Qwen Coder and CodeLlama are optimized for code
   - General models (Llama, Mistral) work but may be less accurate

2. **Adjust Context Window**
   - Larger context windows help with complex templates
   - Qwen and Llama 3.1 support very large contexts (32K-128K tokens)

3. **Temperature Settings**
   - Default is 0.0 for deterministic results
   - Higher temperature (0.3-0.7) for more creative/varied code

4. **Batch Processing**
   - Run multiple small experiments vs one large experiment
   - Easier to debug and analyze results

5. **Model Selection**
   - Start with 7B models to verify setup
   - Move to larger models for higher quality results
   - Compare multiple models on same template set

## Performance Metrics

Track these metrics across providers:
- **Vulnerability Rate**: % of generated code with SQL injection
- **Severity Distribution**: Critical/High/Medium/Low counts
- **CWE Coverage**: Which vulnerability types appear
- **Error Rate**: Failed code generations
- **Generation Speed**: Time per scenario

All metrics are automatically included in the generated reports.
