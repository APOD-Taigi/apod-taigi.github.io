.PHONY: backup

dev:
	pip install -r requirements-dev.txt && \
	pre-commit install
fmt:
	pre-commit run --all-files

backup:
	apod backup -o backup
convert:
	apod convert-blogger-posts-to-markdown -i backup -o content/posts
