# Note: the build context for this dockerfile is actually
# the "Sparrow" project directory, not the docs directory

# Build schema documentation in one layer:
FROM pandoc/core AS schema-builder
# Install additional dependencies
RUN apk add --no-cache --update coreutils python3 && \
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


# Then build the overall documentation site:
FROM node:12-slim AS docs-base
COPY docs/package.json /docs/package.json
WORKDIR /docs
RUN npm --unsafe-perm=true --allow-root install

EXPOSE 3000
COPY --from=schema-builder /build/schema.html /build/schema.html

FROM docs-base AS docs-builder

COPY docs/ /docs/

RUN npm run build

FROM nginx:1.19 AS docs

COPY --from=docs-builder /docs/build /usr/share/nginx/html
COPY ./docs/docs-site.conf /etc/nginx/conf.d/docs-site.conf

EXPOSE 80
