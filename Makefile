.PHONY: install virtualenv ipython clean test pflake8

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

# Executa os testes utilizando o pytest.
test:
	@.venv/bin/pytest -s

# Executa os testes no modo watch.
watch:
	# @.venv/bin/ptw -- -vv -s
	@ls **/*.py | entr pytest

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