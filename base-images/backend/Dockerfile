FROM python:3.9
LABEL version="2.0"

# Install general and build dependencies
# Note: geos and geos-dev are in the community apk repository
RUN apt-get update && apt-get install -y postgresql-client
# RUN apk update \
#  && apk upgrade \
#  && echo http://dl-cdn.alpinelinux.org/alpine/edge/community \
#      >> /etc/apk/repositories \
#  && apk add --no-cache python3-dev libstdc++ openblas \
#       libpq postgresql-dev postgresql-client libxslt-dev bash libc-dev \
#       musl-dev geos geos-dev openblas-dev \
#  && ln -s /usr/include/locale.h /usr/include/xlocale.h \
#  && apk add --no-cache --virtual .build_deps gcc g++ gfortran \
#      openblas-dev libxml2-dev make

COPY ./base-requirements.txt /src/base-requirements.txt
RUN pip install --upgrade pip \
 && pip install --no-cache -r /src/base-requirements.txt

# Delete build deps and test that we can find GEOS C extensions
RUN python -c "import shapely.wkb"
