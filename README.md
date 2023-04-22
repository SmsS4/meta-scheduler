# Alembic

## New revision
```shell
alembic revision -m "Desc"
```
## Upgrade to head
```shell
alembic upgrade head
```

# [Poetry](https://python-poetry.org/)

## Usefull commands
```shell
poetry shell
poetry add fastapi
poetry add pytest --dev
poetry install
poetry install --no-dev
poetry update
poetry run
peotry remove fastapi
poetry remove pytest --no-dev
poetry [command] -vvv
```

## [Zsh plugin](https://github.com/darvid/zsh-poetry)
Automatically activates virtual environments created by Poetry when changing to a project directory with a valid `pyproject.toml`

## Tips
It's better to specify version of package to install to prevent to speedup resolving dependencies
```shell
poetry add package_name==1.18
```
instead of
```shell
poetry add package_name
```

or you can use these commands
```shell
PACKAGE=mypy && poetry add $PACKAGE=`poetry add $PACKAGE --dry-run 2>/dev/null | head -n1 | awk '{print substr($3, 2)}'`
```
---

# Precommit
```shell
poetry run pre-commit run --all-files
```
or
```shell
pre-commit run --all-files
```
## hooks:
  - [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
    checks structures of files like toml, ast, and ...
  - [reorder python imports](https://github.com/asottile/reorder_python_imports)
    Reorder python imports to reduct merge conflict
  - [pycln](https://github.com/hadialqattan/pycln)
    A formatter for finding and removing unused import statements
  - [pyupgrade](https://github.com/asottile/pyupgrade)
    Upgrade python syntax. for example change `dict()` to `{}`
  - [black](https://github.com/psf/black)
    Code formatter
  - [mypy](https://github.com/pre-commit/mirrors-mypy)
    Checks types
  - [pylint](https://github.com/pycqa/pylint)
    Code analyzer
  - [bandit](https://github.com/PyCQA/bandit)
    Security analyzer
---
# Config
You can use `environments variable` or `.env file` or `settings.toml file` to set configs
---

# Test
Write your fixtures in `conftest.py` and your helper functions in `utils.py`
```shell
poetry run python -s -m pytest tests -o log_cli=true
```
You can skip using docker with `--docker false`
```shell
poetry run python -s -m pytest tests --docker false -o log_cli=true
```

# Production
To set environment for production you can use `export ENV_FOR_DYNACONF=production`
