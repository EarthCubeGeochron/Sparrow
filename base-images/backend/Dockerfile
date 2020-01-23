FROM python:3.8-alpine
LABEL version="1.1"

# Install general and build dependencies
RUN apk update \
 && apk upgrade \
 && apk add --no-cache python3-dev libstdc++ openblas \
      libpq postgresql-dev postgresql-client libxslt-dev bash \
 && apk add --no-cache --virtual .build_deps gcc g++ gfortran \
      musl-dev python3-dev openblas-dev libxml2-dev make \
 && ln -s /usr/include/locale.h /usr/include/xlocale.h

###
# Install GEOS for shapely, and the bash shell
###
WORKDIR /src
ENV GEOS_VERSION 3.8.0
# Install geos
ADD http://download.osgeo.org/geos/geos-$GEOS_VERSION.tar.bz2 /src/geos-$GEOS_VERSION.tar.bz2
RUN tar jxf geos-$GEOS_VERSION.tar.bz2 \
 && cd /src/geos-$GEOS_VERSION \
 && ./configure \
 && make \
 && make install \
 && rm -rf /src

COPY ./base-requirements.txt /src/base-requirements.txt
RUN pip install --no-cache -r /src/base-requirements.txt

RUN rm -rf /src \
 && rm /usr/include/xlocale.h \
 && apk del .build_deps
