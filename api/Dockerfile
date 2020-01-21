FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ARG BUILD_ENV=production

WORKDIR /app
ENV PYTHONPATH=/app/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && \
    pip install poetry==1.0.2 && \
    poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/
RUN env
RUN poetry install $(test "$BUILD_ENV" = "production" && echo "--no-dev") --no-interaction --no-ansi

COPY ./app /app/app
