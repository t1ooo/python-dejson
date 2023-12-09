.PHONY: install
install:
	poetry install


.PHONY: test
test:
	poetry run pytest


.PHONY: example
example:
	poetry run python -m examples.example