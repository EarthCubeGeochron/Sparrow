FROM sparrowdata/backend-base:1.1 AS main
# Multi-stage build of Sparrow backend.

COPY ./requirements.txt /install/requirements.txt
RUN pip install --no-cache -r /install/requirements.txt

COPY ./docker.cfg /config/docker.cfg
# These values should not change between installations
ENV SPARROW_BACKEND_CONFIG=/config/docker.cfg

# Make sure we don't litter our mounted code directories
# with useless bytecode
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./docker-scripts/run /bin
RUN mkdir /app
WORKDIR /app

## Copy app core
COPY ./setup.py /app
COPY ./sparrow /app/sparrow
COPY ./core_plugins /app/core_plugins

RUN pip install -e .

CMD ["/bin/run"]

# Create a extension to the base image with testing frameworks defined
FROM main AS testing

COPY ./test-requirements.txt /install/test-requirements.txt
RUN pip install --no-cache -r /install/test-requirements.txt

COPY ./docker-scripts/run-tests /bin
CMD ["/bin/run-tests"]
