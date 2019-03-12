FROM python:3.7-alpine

COPY ./docker-scripts/build-deps /install/build-deps
RUN /install/build-deps
COPY ./backend/requirements.txt /install/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /install/requirements.txt

COPY ./config/docker.cfg /config/docker.cfg
ENV SPARROW_CONFIG=/config/docker.cfg

COPY ./docker-scripts/run /bin
COPY ./bin/import-vocabularies /bin
EXPOSE 5000
WORKDIR /app
CMD ["/bin/run"]
