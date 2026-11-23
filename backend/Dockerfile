FROM python:3.12-bookworm AS main
# Multi-stage build of Sparrow backend.

## Git is required for the PyChron importer;
## the PostgreSQL client for migrations and backups
RUN apt-get update && \
  apt-get install -y git postgresql-client && \
  pip install "poetry==1.8.5" && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app

# First copy only requirements, so that dependencies are cached between builds.
COPY poetry.lock pyproject.toml /app/

RUN mkdir -p /app/loader/sparrow/loader && touch /app/loader/sparrow/loader/__init__.py
COPY loader/pyproject.toml /app/loader/
COPY loader/README.md /app/loader/

# Project initialization:
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY ./docker.cfg /config/docker.cfg
# These values should not change between installations
ENV SPARROW_BACKEND_CONFIG=/config/docker.cfg

# Make sure we don't litter our mounted code directories
# with useless bytecode
ENV PYTHONDONTWRITEBYTECODE=1

# This warning can get confused with an error,
# but it's just pip being self-important
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY ./docker-scripts/* /bin/

## Copy app core
COPY ./ /app/

RUN poetry install --no-interaction --no-ansi 

# Copy command-line options to a place where they can be easily accessed
# by the wrapper CLI.
RUN SPARROW_SECRET_KEY=test /app/sparrow/core/__main__.py get-cli-info > /run/cli-info.json

CMD ["/bin/run"]

FROM main AS testing

# For right now, the testing target is the same as the "main" target, but
# we could grab or create additional artifacts or fixtures here.
