#!/bin/bash

# Quick start script for multi-provider experiment setup
# This script helps set up and run experiments with different LLM providers

set -e

echo "=============================================="
echo "Multi-Provider SQL Vulnerability Experiment"
echo "Setup & Quick Start"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check Python installation
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    exit 1
fi
print_success "pip3 found"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt --quiet
print_success "Python dependencies installed"

# Check if .env file exists
echo ""
if [ ! -f .env ]; then
    print_warning ".env file not found"
    echo ""
    echo "Creating .env template..."
    cat > .env << 'EOF'
# API Keys
CLAUDE_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Ollama server URL (default: http://localhost:11434)
# OLLAMA_BASE_URL=http://localhost:11434
EOF
    print_success ".env template created"
    echo ""
    print_info "Please edit .env and add your API keys:"
    print_info "  - CLAUDE_API_KEY is required for vulnerability analysis"
    print_info "  - OPENAI_API_KEY is required only if using OpenAI provider"
    echo ""
else
    print_success ".env file exists"
fi

# Check for Claude API key
if grep -q "your_claude_api_key_here" .env 2>/dev/null; then
    print_warning "CLAUDE_API_KEY not configured in .env"
    print_info "Please add your Claude API key to .env file"
fi

# Check which providers can be used
echo ""
echo "Checking available providers..."

# Check OpenAI
if grep -q "OPENAI_API_KEY=" .env 2>/dev/null && ! grep -q "your_openai_api_key_here" .env; then
    print_success "OpenAI: Configured (API key found)"
    OPENAI_AVAILABLE=true
else
    print_warning "OpenAI: Not configured (add OPENAI_API_KEY to .env)"
    OPENAI_AVAILABLE=false
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    print_success "Ollama: Installed"
    
    # Check if Ollama server is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama: Server running"
        
        # List available models
        MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; print('\n'.join([m['name'] for m in json.load(sys.stdin)['models']]))" 2>/dev/null || echo "")
        
        if [ -n "$MODELS" ]; then
            print_success "Ollama: Models available:"
            echo "$MODELS" | while read -r model; do
                echo "    - $model"
            done
            OLLAMA_AVAILABLE=true
        else
            print_warning "Ollama: No models pulled yet"
            OLLAMA_AVAILABLE=false
        fi
    else
        print_warning "Ollama: Server not running (start with 'ollama serve')"
        OLLAMA_AVAILABLE=false
    fi
else
    print_warning "Ollama: Not installed (visit https://ollama.ai)"
    OLLAMA_AVAILABLE=false
fi

# Interactive setup menu
echo ""
echo "=============================================="
echo "What would you like to do?"
echo "=============================================="
echo "1. Run experiment with OpenAI GPT-3.5"
echo "2. Run experiment with Ollama (local model)"
echo "3. Install/Setup Ollama"
echo "4. Pull recommended Ollama models"
echo "5. Exit"
echo ""
read -p "Enter your choice [1-5]: " choice

case $choice in
    1)
        if [ "$OPENAI_AVAILABLE" = false ]; then
            print_error "OpenAI is not configured. Please add OPENAI_API_KEY to .env"
            exit 1
        fi
        
        echo ""
        read -p "Number of test scenarios [50]: " num_samples
        num_samples=${num_samples:-50}
        
        echo ""
        print_info "Running experiment with OpenAI GPT-3.5 ($num_samples scenarios)..."
        python3 src/code_completion_main_multi.py $num_samples
        ;;
        
    2)
        if [ "$OLLAMA_AVAILABLE" = false ]; then
            print_error "Ollama is not properly set up"
            print_info "Please:"
            print_info "  1. Install Ollama (option 3)"
            print_info "  2. Start Ollama server: ollama serve"
            print_info "  3. Pull a model (option 4)"
            exit 1
        fi
        
        echo ""
        echo "Available models:"
        echo "$MODELS" | nl
        echo ""
        read -p "Enter model name [qwen2.5-coder:7b]: " model
        model=${model:-qwen2.5-coder:7b}
        
        echo ""
        read -p "Number of test scenarios [50]: " num_samples
        num_samples=${num_samples:-50}
        
        echo ""
        print_info "Running experiment with Ollama $model ($num_samples scenarios)..."
        python3 src/code_completion_main_multi.py $num_samples --provider ollama --model $model
        ;;
        
    3)
        echo ""
        print_info "Installing Ollama..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            print_info "macOS detected - downloading Ollama installer..."
            curl -fsSL https://ollama.ai/install.sh | sh
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            print_info "Linux detected - installing Ollama..."
            curl -fsSL https://ollama.ai/install.sh | sh
        else
            print_warning "Unsupported OS. Please visit https://ollama.ai/download"
            exit 1
        fi
        
        print_success "Ollama installed!"
        print_info "Start the server with: ollama serve"
        ;;
        
    4)
        if ! command -v ollama &> /dev/null; then
            print_error "Ollama is not installed. Please install it first (option 3)"
            exit 1
        fi
        
        echo ""
        echo "Recommended models for code generation:"
        echo "1. qwen2.5-coder:7b    (4.7GB - Good quality, fast)"
        echo "2. qwen2.5-coder:14b   (8.9GB - Better quality, slower)"
        echo "3. codellama:7b        (3.8GB - Fast, decent quality)"
        echo "4. codellama:13b       (7.4GB - Better quality)"
        echo "5. All of the above"
        echo ""
        read -p "Which model(s) to pull [1]: " model_choice
        model_choice=${model_choice:-1}
        
        case $model_choice in
            1)
                ollama pull qwen2.5-coder:7b
                ;;
            2)
                ollama pull qwen2.5-coder:14b
                ;;
            3)
                ollama pull codellama:7b
                ;;
            4)
                ollama pull codellama:13b
                ;;
            5)
                print_info "Pulling all recommended models (this will take a while)..."
                ollama pull qwen2.5-coder:7b
                ollama pull qwen2.5-coder:14b
                ollama pull codellama:7b
                ollama pull codellama:13b
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
        
        print_success "Model(s) pulled successfully!"
        ;;
        
    5)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_success "Done!"
