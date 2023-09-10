FROM postgis/postgis:14-3.3

WORKDIR /tmp/install

# Install unzip
RUN apt-get update && \
    apt-get install -y unzip gcc make postgresql-server-dev-14 && \
    rm -rf /var/lib/apt/lists/*


# Install PGMemento
ADD https://github.com/pgMemento/pgMemento/releases/download/v0.7.4/pgmemento-0.7.4.zip /tmp/install/pgmemento-0.7.4.zip
RUN unzip pgmemento-0.7.4.zip && cd pgmemento-0.7.4 && make && make install

# Install pg_safeupdate
ADD https://github.com/eradman/pg-safeupdate/archive/refs/tags/1.4.zip /tmp/install/pg-safeupdate-1.4.zip
RUN unzip pg-safeupdate-1.4.zip && cd pg-safeupdate-1.4 && make && make install

RUN rm -rf /tmp/install && apt-get remove -y unzip make gcc postgresql-server-dev-14 && apt-get autoremove -y