.PHONY: setup test run draft clean

setup: ## install deps
	pip install -r requirements.txt && npm ci

test: ## run all tests
	pytest -q

run: ## run pipeline on sample
	python -m src.run --input inbox/chat.html --create-draft=false

draft: ## run with draft creation
	python -m src.run --input inbox/chat.html --create-draft=true

clean: ## clean dist and cache
	rm -rf dist/ __pycache__/ .pytest_cache/
