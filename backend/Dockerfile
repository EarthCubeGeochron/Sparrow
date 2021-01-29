FROM sparrowdata/backend-base:1.2 AS main
# Multi-stage build of Sparrow backend.

## Git is required for the PyChron importer
RUN apk update && apk add git

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

# For graphing the database schema
RUN git clone https://github.com/davenquinn/sadisplay.git /ext/sadisplay \
  && pip install -e /ext/sadisplay

COPY ./docker-scripts/* /bin/
RUN mkdir /app
WORKDIR /app

## Copy app core
COPY ./ /app/

RUN pip install -e utils && pip install -e .

# Copy command-line options to a place where they can be easily accessed
# by the wrapper CLI.
RUN SPARROW_SECRET_KEY=test /app/sparrow/__main__.py get-cli-info > /run/cli-info.json

CMD ["/bin/run"]

FROM main AS testing

# For right now, the testing target is the same as the "main" target, but
# we could grab or create additional artifacts or fixtures here.
