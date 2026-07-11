install:
	uv sync

run:
	uv run main.py $(ARGS)

debug:
	uv run -m pdb main.py $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".vscode" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs


.PHONY: install run debug clean lint lint-strict