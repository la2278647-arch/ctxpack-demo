.PHONY: run test lint format seed export

run:
	uvicorn hello_service.app:app --reload --port 8000

test:
	pytest

lint:
	ruff check hello_service tests

format:
	ruff format hello_service tests

seed:
	python -m scripts.seed

export:
	python -m scripts.export --out data/exported.json
