FROM sparrowdata/backend-base:1.2 AS main
# Multi-stage build of Sparrow backend.

COPY ./requirements.txt /install/requirements.txt
RUN pip install --no-cache "https://github.com/djrobstep/sqlakeyset/zipball/fec6936"
RUN pip install --no-cache -r /install/requirements.txt

COPY ./docker.cfg /config/docker.cfg
# These values should not change between installations
ENV SPARROW_BACKEND_CONFIG=/config/docker.cfg

# Make sure we don't litter our mounted code directories
# with useless bytecode
ENV PYTHONDONTWRITEBYTECODE=1

# This warning can get confused with an error,
# but it's just pip being self-important
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# Disable caching to slim down image
ENV PIP_NO_CACHE_DIR=1

COPY ./docker-scripts/* /bin/
RUN mkdir /app
WORKDIR /app

## Copy app core
COPY ./setup.py /app
COPY ./sparrow /app/sparrow
COPY ./core_plugins /app/core_plugins

RUN pip install -e .

CMD ["/bin/run"]

FROM main AS testing

COPY ./tests /app/tests
