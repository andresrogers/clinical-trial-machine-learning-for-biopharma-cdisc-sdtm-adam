.PHONY: setup-python setup-r validate fmt lint test

setup-python:
	pip install -e .[dev,reports]

setup-r:
	Rscript install_r_packages.R

validate:
	python -c "import pandas, pyarrow, duckdb, sklearn, lifelines, shap, plotly, jinja2, pandera; print('python environment ok')"

fmt:
	ruff format .

lint:
	ruff check .

test:
	pytest
