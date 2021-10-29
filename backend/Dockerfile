FROM ghcr.io/earthcubegeochron/sparrow/backend-base:2.0 AS main
# Multi-stage build of Sparrow backend.

## Git is required for the PyChron importer
RUN apt update && \
  apt install -y git && \
  pip install "poetry==1.1.10" && \
  rm -rf /var/lib/apt/lists/*

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN --mount=type=cache,target=/root/.cache \
  poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

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
RUN mkdir /app
WORKDIR /app

## Copy app core
COPY ./ /app/

RUN poetry install --no-interaction --no-ansi 

# Copy command-line options to a place where they can be easily accessed
# by the wrapper CLI.
RUN SPARROW_SECRET_KEY=test /app/sparrow/__main__.py get-cli-info > /run/cli-info.json

CMD ["/bin/run"]

FROM main AS testing

# For right now, the testing target is the same as the "main" target, but
# we could grab or create additional artifacts or fixtures here.
