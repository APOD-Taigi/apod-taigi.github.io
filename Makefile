
dev:
	pip install -r requirements-dev.txt && \
	pre-commit install
fmt:
	pre-commit run --all-files
