.PHONY: install virtualenv ipython clean test pflake8 docs docs-serve build publish-test publish

install:
	@echo "Installing for dev environment"
	@.venv/bin/python -m pip install -e '.[test,dev]'

virtualenv:
	@echo "Creating virtualenv"
	@python3 -m venv .venv
	@echo "Virtualenv created and activated"

ipython:
	@.venv/bin/ipython

lint:
	@.venv/bin/mypy --ignore-missing-imports dundie
	@.venv/bin/pflake8

fmt:
	@.venv/bin/isort --profile=black -m 3 dundie tests integration
	@.venv/bin/black dundie tests integration

test:
	@.venv/bin/pytest -s --cov=dundie --forked
	@.venv/bin/coverage xml
	@.venv/bin/coverage html

watch:
	# @.venv/bin/ptw -- -vv -s
	@ls **/*.py | entr pytest --cov=dundie --forked
	@.venv/bin/coverage xml
	@.venv/bin/coverage html

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

docs:
	@.venv/bin/mkdocs build --clean

docs-serve:
	@.venv/bin/mkdocs serve

build:
	@python setup.py sdist bdist_wheel

publish-test:
	@twine upload --repository testpypi dist/*

publish:
	@twine upload dist/*