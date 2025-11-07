# Multi-Provider LLM Architecture - Implementation Summary

## Overview

The SQL vulnerability experiment has been enhanced with a **multi-provider architecture** that supports running code generation experiments with different LLM providers while maintaining the same vulnerability analysis framework.

## What Was Changed

### New Architecture Components

#### 1. Base Abstraction Layer
**File:** `src/api/base_llm_client.py`

Created an abstract base class `BaseLLMClient` that defines the interface all LLM providers must implement:
```python
class BaseLLMClient(ABC):
    @abstractmethod
    def get_sql_code(prompt, max_tokens, temperature) -> str
    
    @abstractmethod
    def get_model_name() -> str
    
    @abstractmethod
    def get_provider_name() -> str
```

This ensures consistency across all providers and makes the system extensible.

#### 2. Ollama Client Implementation
**File:** `src/api/ollama_client.py`

New client for running local LLMs via Ollama:
- Supports Qwen, Llama, CodeLlama, DeepSeek, Mistral, and other Ollama models
- Uses LangChain for integration
- Includes predefined model configurations with recommended context windows
- No API key required (runs locally)

**Key Features:**
- Auto-detects optimal context window per model
- Configurable base URL for remote Ollama servers
- Built-in model presets (e.g., `OllamaModels.QWEN_CODER_7B`)

#### 3. Updated OpenAI Client
**File:** `src/api/openai_client.py`

Modified to inherit from `BaseLLMClient`:
- Implements required abstract methods
- Maintains backward compatibility
- Returns provider metadata for reporting

### Modified Components

#### 4. Provider-Agnostic Runner
**File:** `src/code_completion_runner.py`

Updated `CodeCompletionRunner` to work with any `BaseLLMClient`:

**Before:**
```python
def __init__(self, openai_client, claude_client, ...):
    self.openai_client = openai_client
```

**After:**
```python
def __init__(self, code_generator_client: BaseLLMClient, claude_client, ...):
    self.code_generator = code_generator_client
    self.code_gen_provider = code_generator_client.get_provider_name()
    self.code_gen_model = code_generator_client.get_model_name()
```

**Changes:**
- Accepts any `BaseLLMClient` implementation
- Tracks provider/model metadata
- Reports provider info in experiment output
- Updates all references from `openai_client` to `code_generator`

#### 5. New Multi-Provider Main Script
**File:** `src/code_completion_main_multi.py`

Complete rewrite of the main entry point with:

**Command-line Interface:**
```bash
python src/code_completion_main_multi.py [num_samples] [--provider PROVIDER] [--model MODEL] [options]
```

**Key Features:**
- Provider selection: `--provider openai` or `--provider ollama`
- Model selection: `--model gpt-3.5-turbo` or `--model qwen2.5-coder:7b`
- Custom experiment naming: `--name my-experiment`
- Ollama server URL: `--ollama-url http://custom-url:11434`
- Comprehensive help and examples

**Provider Initialization:**
- Automatic client initialization based on provider argument
- Validation of API keys and server availability
- Clear error messages with remediation steps

### Supporting Files

#### 6. Dependencies
**File:** `requirements.txt`

Added LangChain dependencies:
```
langchain-ollama>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.20
```

#### 7. Documentation

**MULTI_PROVIDER_GUIDE.md** - Comprehensive guide covering:
- Architecture overview
- Setup instructions for each provider
- Usage examples and commands
- Model recommendations and comparisons
- Performance metrics
- Troubleshooting guide
- Adding new providers

**quickstart_multi.sh** - Interactive setup script:
- Checks prerequisites
- Validates .env configuration
- Detects available providers
- Interactive menu for common tasks
- Automated Ollama installation and model pulling

## Usage Examples

### OpenAI (Cloud)
```bash
# Default GPT-3.5
python src/code_completion_main_multi.py 50

# GPT-4
python src/code_completion_main_multi.py 50 --model gpt-4
```

### Ollama (Local)
```bash
# Qwen Coder (recommended for code)
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b

# CodeLlama
python src/code_completion_main_multi.py 50 --provider ollama --model codellama:13b

# Llama 3.1
python src/code_completion_main_multi.py 30 --provider ollama --model llama3.1:8b
```

### Comparative Experiments
```bash
# Run with different providers and compare
python src/code_completion_main_multi.py 50 --name gpt35-baseline
python src/code_completion_main_multi.py 50 --provider ollama --model qwen2.5-coder:7b --name qwen-baseline
python src/code_completion_main_multi.py 50 --provider ollama --model codellama:7b --name codellama-baseline
```

## Output Changes

### Experiment Directory Naming
**Before:** `experiments/run_YYYYMMDD_HHMMSS/`

**After:** `experiments/<provider>_<model>_run_YYYYMMDD_HHMMSS/`

Examples:
- `experiments/openai_gpt-3.5-turbo_run_20251105_120000/`
- `experiments/ollama_qwen2.5-coder-7b_run_20251105_120000/`

### Report Metadata

Reports now include provider information:

```markdown
## Experiment Configuration

- **Code Generator:** Ollama (qwen2.5-coder:7b)
- **Vulnerability Analyzer:** Claude (with OWASP SQL reference)
- **Analysis Approach:** Cached system prompts for efficiency
```

## Backward Compatibility

### Original Script Maintained
**File:** `src/code_completion_main.py`

The original OpenAI-only script is **unchanged** and still works:
```bash
python src/code_completion_main.py 50  # Still works as before
```

### Migration Path
Users can:
1. Continue using the original script
2. Gradually migrate to multi-provider script
3. Run both for comparison

## Extension Points

### Adding New Providers

To add a new provider (e.g., Anthropic, Cohere, HuggingFace):

1. **Create Client Class:**
```python
# src/api/new_provider_client.py
from .base_llm_client import BaseLLMClient

class NewProviderClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str):
        # Initialize
        pass
    
    def get_sql_code(self, prompt: str, max_tokens: int, temperature: float) -> str:
        # Implement
        pass
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "NewProvider"
```

2. **Update Main Script:**
```python
# In code_completion_main_multi.py
def initialize_code_generator(args):
    if args.provider == "newprovider":
        api_key = os.getenv("NEWPROVIDER_API_KEY")
        return NewProviderClient(api_key=api_key, model=args.model)
```

3. **Update Argument Parser:**
```python
parser.add_argument(
    "--provider",
    choices=["openai", "ollama", "newprovider"],
    ...
)
```

## Benefits

### 1. **Flexibility**
- Test code generation with multiple models
- Compare vulnerability rates across providers
- Choose between cloud and local execution

### 2. **Cost Efficiency**
- Use free local models via Ollama
- Reduce API costs for large experiments
- Mix and match based on budget

### 3. **Research Value**
- Compare LLM security characteristics
- Identify provider-specific vulnerability patterns
- Benchmark model performance on security

### 4. **Privacy**
- Run experiments entirely locally
- No code sent to external APIs (with Ollama)
- Suitable for sensitive codebases

### 5. **Extensibility**
- Clean abstraction for adding providers
- Minimal code changes required
- Consistent interface across providers

## Recommended Model Combinations

### For Research/Comparison
| Provider | Model | Why |
|----------|-------|-----|
| OpenAI | gpt-3.5-turbo | Industry baseline |
| OpenAI | gpt-4 | Best quality reference |
| Ollama | qwen2.5-coder:7b | Best local code model |
| Ollama | codellama:13b | Alternative code model |
| Ollama | llama3.1:8b | General model comparison |

### For Production Testing
- **Cloud:** OpenAI GPT-4 (highest quality)
- **Local:** Qwen 2.5 Coder 14B (best local quality)
- **Fast:** CodeLlama 7B or Qwen Coder 7B

### For Budget-Conscious Research
- **Primary:** Ollama Qwen Coder 7B (free, good quality)
- **Validation:** OpenAI GPT-3.5 (low cost, industry standard)

## Performance Characteristics

### OpenAI
- **Speed:** Very fast (API latency)
- **Quality:** High (GPT-3.5) to Very High (GPT-4)
- **Cost:** $0.50-$3 per million tokens
- **Requirements:** API key, internet

### Ollama (7B models)
- **Speed:** Fast (~1-2 sec per request)
- **Quality:** High for code-specific models
- **Cost:** Free (after hardware)
- **Requirements:** 8GB+ RAM, ~5GB disk per model

### Ollama (13-14B models)
- **Speed:** Medium (~3-5 sec per request)
- **Quality:** Very High
- **Cost:** Free (after hardware)
- **Requirements:** 16GB+ RAM, ~8GB disk per model

## Testing Checklist

Before running experiments:

- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] Claude API key set (required for all experiments)
- [ ] OpenAI API key set (if using OpenAI provider)
- [ ] Ollama installed and running (if using Ollama provider)
- [ ] Ollama models pulled (if using Ollama provider)
- [ ] SQL reference file present (`checks/sql/sql_owasp_reference.md`)

Quick validation:
```bash
./quickstart_multi.sh  # Interactive setup and validation
```

## Known Limitations

1. **Ollama Requires Local Resources**
   - 7B models need 8GB+ RAM
   - 13-14B models need 16GB+ RAM
   - Larger models significantly slower

2. **Provider-Specific Quirks**
   - Different models have different output formats
   - Some models more verbose than others
   - Quality varies significantly

3. **Analysis Always Uses Claude**
   - Only code generation is multi-provider
   - Vulnerability analysis always via Claude API
   - Could be extended to support local analysis models

## Future Enhancements

Potential additions:
1. Support for more providers (Anthropic, Cohere, HuggingFace)
2. Multi-provider analysis (not just code generation)
3. Ensemble approaches (multiple models vote)
4. Fine-tuned models for SQL security
5. RAG-enhanced code generation (like in rag_local.py)
6. Streaming responses for faster perceived performance
7. GPU acceleration for local models
8. Distributed Ollama for scaling

## Migration from Original Setup

For users of the original experiment:

### What Stays the Same
- Template generation (still uses Claude)
- Vulnerability analysis (still uses Claude with SQL reference)
- Output format (JSON + Markdown reports)
- Results structure and metrics

### What's New
- Code generation provider is selectable
- New command-line interface
- Provider metadata in reports
- Support for local models

### Migration Steps
1. Install new dependencies: `pip install -r requirements.txt`
2. Try new script: `python src/code_completion_main_multi.py 5 --name test`
3. Compare with original: `python src/code_completion_main.py 5`
4. Switch fully when comfortable

## Conclusion

The multi-provider architecture maintains all existing functionality while adding significant flexibility for research and practical use. The clean abstraction makes it easy to add new providers, and the comprehensive tooling (guides, scripts) makes it accessible for both new and experienced users.

The system is production-ready for comparative LLM security research while remaining simple enough for quick experiments.
