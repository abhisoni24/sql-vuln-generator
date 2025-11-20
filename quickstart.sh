#!/bin/bash
# Quick start script for LLM vulnerability experiments

echo "🚀 LLM Code Generation & Vulnerability Analysis"
echo "=============================================="

# Check if we're in the right environment
if [[ "$CONDA_DEFAULT_ENV" != "sql-vuln" ]]; then
    echo "⚠️  Warning: Not in sql-vuln conda environment"
    echo "   Run: conda activate sql-vuln"
    echo ""
fi

# Check for API keys
echo "🔑 Checking API keys..."
if [[ -z "$CLAUDE_API_KEY" ]]; then
    echo "❌ CLAUDE_API_KEY not set"
else
    echo "✅ Claude API key found"
fi

if [[ -z "$GEMINI_API_KEY" ]] && [[ -z "$GOOGLE_API_KEY" ]]; then
    echo "❌ GEMINI_API_KEY/GOOGLE_API_KEY not set"
else
    echo "✅ Gemini API key found"
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "❌ OPENAI_API_KEY not set"
else
    echo "✅ OpenAI API key found"
fi

echo ""
echo "📋 Available experiments:"
echo "  1. Claude → Gemini (recommended)"
echo "  2. Gemini → Claude (baseline)"
echo "  3. OpenAI → Claude"
echo ""

read -p "Choose experiment (1-3): " choice

case $choice in
    1)
        echo "Running Claude → Gemini experiment..."
        python main.py -g claude -a gemini
        ;;
    2)
        echo "Running Gemini → Claude experiment..."
        python main.py -g gemini -a claude
        ;;
    3)
        echo "Running OpenAI → Claude experiment..."
        python main.py -g openai -a claude
        ;;
    *)
        echo "Invalid choice. Run: python main.py --help"
        ;;
esac
