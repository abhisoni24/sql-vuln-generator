# LLM Experiment Simplification Summary

## What Was Simplified

### Before (Complex)
- Multiple similar scripts: `run_vulnerable_scenarios_experiment.py`, `run_vulnerable_scenarios_experiment_claude_gemini.py`, etc.
- Complex `CodeCompletionRunner` with hardcoded Claude dependency
- Scattered experiment results in various directories
- No unified interface for LLM providers
- Hardcoded configurations

### After (Simple)
- Single entry point: `python main.py`
- Unified `LLMFactory` for all providers
- Simple `SimpleExperimentRunner` with clean interface
- Organized results in `experiments/` subdirectories
- Configuration-driven experiments

## Key Improvements

### 1. Single Command Interface
```bash
# Old way - multiple scripts
python src/run_vulnerable_scenarios_experiment.py
python src/run_vulnerable_scenarios_experiment_claude_gemini.py

# New way - one command
python main.py --generator claude --analyzer gemini
```

### 2. LLM Factory Pattern
```python
# Old way - direct imports
from api.claude_client import ClaudeClient
from api.gemini_client import GeminiClient

# New way - factory
from api.llm_factory import LLMFactory
claude = LLMFactory.create('claude')
gemini = LLMFactory.create('gemini')
```

### 3. Clean Experiment Runner
- Removed complex dependencies
- Unified interface for all LLM combinations
- Automatic result saving and reporting
- Better error handling

### 4. Organized Structure
```
experiments/
├── configs/     # Future configuration files
├── results/     # JSON results
└── reports/     # Markdown reports
```

## Usage Examples

### Basic Experiments
```bash
# Claude generates, Gemini analyzes
python main.py -g claude -a gemini

# Gemini generates, Claude analyzes
python main.py -g gemini -a claude

# OpenAI generates, Claude analyzes
python main.py -g openai -a claude
```

### Advanced Usage
```bash
# Custom models
python main.py -g claude -m claude-3-5-haiku -a gemini -n gemini-2.5-pro

# Custom experiment name
python main.py -g claude -a gemini --name my_test_experiment

# Different output directory
python main.py -g claude -a gemini --output my_experiments
```

## Files Changed/Created

### New Files
- `main.py` - Single entry point
- `src/api/llm_factory.py` - LLM factory pattern
- `src/simple_experiment_runner.py` - Simplified experiment runner
- `README.md` - Updated documentation

### Modified Files
- `src/api/base_llm_client.py` - Added send_prompt_with_system method
- `src/api/claude_client.py` - Now inherits from BaseLLMClient
- `src/api/gemini_client.py` - Added analysis methods
- `src/api/openai_client.py` - Added send_prompt_with_system method
- `quickstart.sh` - Updated for new interface

### Preserved Files
- All existing experiment results
- Original complex scripts (for reference)
- Documentation and fixtures

## Benefits

1. **Simplicity**: One command to run any experiment combination
2. **Extensibility**: Easy to add new LLM providers
3. **Maintainability**: Clean, modular code structure
4. **Consistency**: Unified interface across all components
5. **Usability**: Intuitive command-line interface

## Migration Guide

### For Users
```bash
# Old way
python src/run_vulnerable_scenarios_experiment.py --model gemini-2.5-pro

# New way
python main.py --generator gemini --analyzer claude
```

### For Developers
```python
# Old way
from code_completion_runner import CodeCompletionRunner
runner = CodeCompletionRunner(gemini_client, claude_client)

# New way
from simple_experiment_runner import SimpleExperimentRunner
runner = SimpleExperimentRunner('gemini', 'claude')
```