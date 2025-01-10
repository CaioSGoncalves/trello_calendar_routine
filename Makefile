run:
	@echo "Running for today"
	uv run src/main.py --target today

run-monday:
	@echo "Running for monday"
	uv run src/main.py --target monday
