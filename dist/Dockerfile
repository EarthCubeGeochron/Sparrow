FROM python:3.7-alpine as base

# Create a "builder" image so that we can build
# dependencies without taking up caching space
FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY ./app/requirements.txt /requirements.txt

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

# Create our actual application image
FROM base

COPY --from=builder /install /usr/local

RUN mkdir /app
COPY ./app/labdata /app/labdata
COPY ./app/import-pipelines /app/import-pipelines

WORKDIR /app

CMD ["python", "-m labdata", "serve"]
