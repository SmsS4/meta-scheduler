FROM python:3.10.10

RUN pip install poetry

WORKDIR /code

COPY glogger /code/glogger/

COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY ./ /code/
