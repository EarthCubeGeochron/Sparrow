# Note: the build context for this dockerfile is actually
# the "Sparrow" project directory, not the docs directory

## Schema Docs
# Build schema documentation in one layer:
FROM pandoc/core AS schema-builder
# Install additional dependencies
RUN apk add --no-cache --update coreutils python3 cmd:pip3 && \
  pip3 install --upgrade pip setuptools && \
  pip3 install pyparsing

COPY backend/sparrow/database/fixtures/02-tables.sql /sql/input.sql
COPY docs/bin/sql-to-markdown /bin/sql-to-markdown
WORKDIR /docs

RUN mkdir /build && \
cat /sql/input.sql \
| /bin/sql-to-markdown \
| pandoc -f markdown -t html --section-divs \
| sed 's/-- //g' \
| tail -n +2 \
> /build/schema.html && \
test -f /build/schema.html

## Core docs

FROM sparrowdata/backend:1.6 AS core-docs

WORKDIR /docs

COPY ./docs/python-api/requirements.txt /docs/requirements.txt
# Copy images/logos into container
COPY ./docs/static/img/ /docs/_static/img/
RUN pip install --no-cache -r /docs/requirements.txt

ENV BACKEND_ROOT=/app
ENV SPARROW_SECRET_KEY=docs

COPY ./docs/python-api/ /docs/

RUN make html

# Then build the overall documentation site:
FROM node:12-slim AS docs-base

WORKDIR /docs

COPY --from=schema-builder /build/schema.html /build/schema.html
EXPOSE 3000

## WE STOP HERE IN DEVELOPMENT MODE ##
## node_modules are installed on startup against mounted code volume.

# New build stage where we actually install and build

FROM docs-base AS docs-builder

# Copy files needed for installation
COPY docs/package.json /docs/package.json
#COPY docs/package-lock.json /docs/package-lock.json

# Install node modules
RUN npm --unsafe-perm=true --allow-root --loglevel=error install

COPY docs/ /docs/

RUN node_modules/.bin/docusaurus clear && npm run build --no-minify

FROM nginx:1.19 AS docs

# Copy site content into docker container
COPY --from=docs-builder /docs/build /usr/share/nginx/html
COPY --from=core-docs /docs/build/html /usr/share/nginx/html/core

# Copy nginx config into docker container
COPY ./docs/server-config/conf.d/production.conf /etc/nginx/conf.d/default.conf
COPY ./docs/server-config/snippets /etc/nginx/snippets

EXPOSE 80
