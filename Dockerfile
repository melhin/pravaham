FROM python:3.11.7

LABEL org.opencontainers.image.source=https://github.com/melhin/just-another-rss-reader

ARG APP_NAME=pravaham
ARG APP_PATH=/opt/$APP_NAME
ARG PYTHON_VERSION=3.11.7
ARG POETRY_VERSION=1.1.15
ARG PORT=8001


ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_NO_INTERACTION=1

# install deps
RUN apt-get update -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN pip install -U pip setuptools wheel poetry
#ENV PATH="$POETRY_HOME/bin:$PATH;"


WORKDIR /code
COPY ./poetry.lock ./pyproject.toml /code/

RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root


# Collect static files
COPY . /code
RUN DJANGO_SETTINGS_MODULE=pravaham.settings.base python manage.py collectstatic --noinput

EXPOSE ${PORT}

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD ["main"]