#!/bin/bash
# Quick start script for the SQL injection vulnerability experiment

set -e

echo "════════════════════════════════════════════════════════════════"
echo "SQL Injection Vulnerability Experiment - Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo

# Check Python
echo "✓ Checking Python installation..."
python --version

# Check pip
echo "✓ Checking pip..."
pip --version

# Install dependencies
echo
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check .env file
echo
echo "🔐 Checking API keys configuration..."
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found!"
    echo
    echo "Please create a .env file with your API keys:"
    echo
    echo "1. Copy the template:"
    cp .env.example .env 2>/dev/null || echo "   cp .env.example .env"
    echo
    echo "2. Edit the file with your API keys:"
    echo "   nano .env"
    echo
    echo "3. Add your keys:"
    echo "   CLAUDE_API_KEY=sk-ant-your-key-here"
    echo "   OPENAI_API_KEY=sk-your-key-here"
    echo
    exit 1
else
    echo "✓ .env file found"
fi

# Check API keys
if grep -q "sk-ant-your-claude-key-here" .env; then
    echo "❌ CLAUDE_API_KEY not set in .env file"
    exit 1
fi

if grep -q "sk-your-openai-key-here" .env; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    exit 1
fi

echo "✓ API keys configured"

# Create experiments directory
echo
echo "📁 Creating experiments directory..."
mkdir -p experiments

# Run the experiment
echo
echo "════════════════════════════════════════════════════════════════"
echo "Starting experiment..."
echo "════════════════════════════════════════════════════════════════"
echo

python -m src.experiment_main 20

echo
echo "════════════════════════════════════════════════════════════════"
echo "✓ Experiment complete!"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Check the 'experiments' directory for:"
echo "  - experiment_results.json (raw data)"
echo "  - REPORT.md (detailed report)"
echo "  - PNG files (visualizations)"
echo
