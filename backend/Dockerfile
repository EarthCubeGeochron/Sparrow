FROM sparrowdata/backend-base:1.0

COPY ./requirements.txt /install/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /install/requirements.txt

RUN apk add --no-cache bash

COPY ./docker.cfg /config/docker.cfg
# These values should not change between installations
ENV SPARROW_BACKEND_CONFIG=/config/docker.cfg

# Make sure we don't litter our mounted code directories
# with useless bytecode
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./docker-scripts/run /bin
EXPOSE 5000
RUN mkdir /app
WORKDIR /app

## Copy API testing data (this could maybe go elsewhere)
COPY ./test_minimal.tavern.yaml /app

## Copy app core
COPY ./setup.py /app
COPY ./sparrow /app/sparrow
RUN pip3 install -e .
RUN mkdir /cache && python3 sparrow --help > /cache/sparrow-help.txt
CMD ["/bin/run"]
