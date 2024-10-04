.PHONY: install virtualenv ipython clean test pflake8 docs docs-serve build publish-test publish

# Comando para instalar as dependências para o ambiente de desenvolvimento.
install:
	@echo "Installing for dev environment"
	@.venv/bin/python -m pip install -e '.[test,dev]'

# Cria um ambiente virtual
virtualenv:
	@echo "Creating virtualenv"
	@python3 -m venv .venv
	@echo "Virtualenv created and activated"

# Executa o ipython a partir do ambiente virtual
ipython:
	@.venv/bin/ipython

# Executa uma análise estática para verificar a escrita do código
lint:
	@.venv/bin/pflake8

# Formato o código com base nos padrões da PEP8
fmt:
	@.venv/bin/black dundie tests integration
	@.venv/bin/isort dundie tests integration

# Executa os testes utilizando o pytest com forked.
test:
	@.venv/bin/pytest -s --forked

# Executa os testes no modo watch com forked.
watch:
	# @.venv/bin/ptw -- -vv -s
	@ls **/*.py | entr pytest --forked

# Limpa arquivos não usados e de cache
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

# Gera a pasta contendo a documentação web
docs:
	@.venv/bin/mkdocs build --clean

# Abre um servidor local para visualizar a documentação web
docs-serve:
	@.venv/bin/mkdocs serve

# Gera os arquivos de build do projeto, em wheel e tar gz
build:
	@python setup.py sdist bdist_wheel

# Publica o projeto no repositório de pacotes de teste
publish-test:
	@twine upload --repository testpypi dist/*

# Publica o projeto no repositório oficial
publish:
	@twine upload dist/*