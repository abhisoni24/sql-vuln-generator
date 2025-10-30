.PHONY: help install setup check run run-large run-small viz analyze clean

help:
	@echo "SQL Injection Vulnerability Experiment - Available Commands"
	@echo ""
	@echo "Setup & Configuration:"
	@echo "  make install      - Install all Python dependencies"
	@echo "  make setup        - Run setup checks and validate configuration"
	@echo "  make check        - Check if everything is configured correctly"
	@echo ""
	@echo "Running Experiments:"
	@echo "  make run          - Run experiment with 20 samples (default)"
	@echo "  make run-small    - Run experiment with 5 samples (fast test)"
	@echo "  make run-large    - Run experiment with 100 samples"
	@echo ""
	@echo "Analysis & Visualization:"
	@echo "  make viz          - Generate visualizations from latest results"
	@echo "  make analyze      - Analyze latest results"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean up temporary files and cache"
	@echo "  make clean-results - Remove all experiment results"
	@echo ""
	@echo "Examples:"
	@echo "  make setup        # First time setup"
	@echo "  make check        # Verify before running"
	@echo "  make run-small    # Quick test run"
	@echo "  make run          # Main experiment"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Installation complete"

setup: install check
	@echo "✓ Setup complete!"

check:
	@echo "Checking configuration..."
	python setup_check.py

run:
	@echo "Running experiment with 20 samples..."
	python -m src.experiment_main 20

run-small:
	@echo "Running quick test with 5 samples..."
	python -m src.experiment_main 5

run-large:
	@echo "Running large experiment with 100 samples (may take 10+ minutes)..."
	python -m src.experiment_main 100

viz:
	@echo "Generating visualizations..."
	python -c "from src.visualizations import generate_all_visualizations; generate_all_visualizations('experiments/experiment_results.json')"

analyze:
	@echo "Analyzing latest results..."
	python -m src.utils.analysis experiments/experiment_results.json

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache/
	@echo "✓ Cleanup complete"

clean-results:
	@echo "Removing all experiment results..."
	@echo "This will delete:"
	@echo "  - experiments/*.json"
	@echo "  - experiments/*.png"
	@echo "  - experiments/REPORT.md"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f experiments/*.json experiments/*.png experiments/REPORT.md; \
		echo "✓ Results cleaned"; \
	else \
		echo "Cancelled"; \
	fi

.DEFAULT_GOAL := help
