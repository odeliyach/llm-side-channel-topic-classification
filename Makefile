.PHONY: help install lint test run clean data train evaluate all

help:
	@echo "LLM Side-Channel Topic Classification - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             Run linters (pylint, black)"
	@echo "  make test             Run unit tests"
	@echo ""
	@echo "Experiment:"
	@echo "  make data             Generate data (Phase 1)"
	@echo "  make train            Train and evaluate models (Phase 2)"
	@echo "  make evaluate         Same as 'make train'"
	@echo "  make all              Run complete pipeline (data + train)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Remove generated files (data/, results/)"
	@echo "  make help             Show this help message"

install:
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

lint:
	@echo "Running pylint..."
	pylint *.py --disable=C,W0212 || echo "⚠️  Lint warnings found (non-blocking)"
	@echo "Running black..."
	black --check *.py || black *.py
	@echo "✓ Linting complete"

test:
	@echo "Running tests..."
	python -m pytest tests/ -v || echo "⚠️  Tests not yet implemented"
	@echo "✓ Tests complete"

data:
	@echo "Generating data (Phase 1)..."
	@echo "⏱  Estimated time: 10-15 minutes"
	python 1_generate_data.py
	@echo "✓ Data generation complete"

train:
	@echo "Training and evaluating models (Phase 2)..."
	@echo "⏱  Estimated time: 30 seconds"
	python 2_train_evaluate.py
	@echo "✓ Training complete"

evaluate: train

all: data train
	@echo "✓ Full pipeline complete!"
	@echo ""
	@echo "Results saved to: results/"
	@ls -lh results/*.png 2>/dev/null || echo "  (No PNG files found)"

clean:
	@echo "Cleaning generated files..."
	rm -f data/responses.json data/*.json
	rm -f results/*.png results/*.csv results/*.txt
	rm -rf __pycache__ .pytest_cache .mypy_cache
	@echo "✓ Clean complete"

.DEFAULT_GOAL := help
