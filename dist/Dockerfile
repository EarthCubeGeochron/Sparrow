FROM python:3.7-alpine

RUN apk update && \
    apk upgrade && \
    apk add --no-cache libstdc++ openblas libpq postgresql-dev && \
    apk add --no-cache --virtual=build_deps g++ gfortran \
                musl-dev python3-dev openblas-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir numpy && \
    pip3 install --no-cache-dir pandas && \
    pip3 install --no-cache-dir psycopg2 && \
    rm /usr/include/xlocale.h && \
    apk del build_deps

COPY ./app/requirements.txt /requirements.txt

RUN pip3 install --no-cache-dir -r /requirements.txt

RUN mkdir /app
COPY ./app/setup.py /app/setup.py
COPY ./app/labdata /app/labdata
COPY ./app/import-pipelines /app/import-pipelines
COPY ./labdata.cfg /app/labdata.cfg
COPY ./_assets /assets
ENV LABDATA_CONFIG=/app/labdata.cfg
WORKDIR /app
RUN pip3 install -e .
EXPOSE 5000
CMD ["python3", "labdata", "serve"]
