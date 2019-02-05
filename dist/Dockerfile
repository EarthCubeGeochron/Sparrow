FROM python:3.7-alpine as base

# Create a "builder" image so that we can build
# dependencies without taking up caching space
FROM base as builder

RUN mkdir /install
WORKDIR /install

RUN apk update && \
    apk upgrade && \
    apk add --no-cache libstdc++ openblas && \
    apk add --no-cache --virtual=build_deps g++ gfortran \
                musl-dev python3-dev openblas-dev postgresql-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    PYTHONUSERBASE=/install pip3 install numpy && \
    PYTHONUSERBASE=/install pip3 install pandas && \
    PYTHONUSERBASE=/install pip3 install psycopg2 && \
    rm /usr/include/xlocale.h && \
    apk del build_deps

COPY ./app/requirements.txt /requirements.txt

RUN PYTHONUSERBASE=/install pip3 install -r /requirements.txt

# Create our actual application image
FROM base

COPY --from=builder /install /usr/local

RUN mkdir /app
COPY ./app/labdata /app/labdata
COPY ./app/import-pipelines /app/import-pipelines

WORKDIR /app

CMD ["python3", "-m labdata", "serve"]
