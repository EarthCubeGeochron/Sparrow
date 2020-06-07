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
FROM node:11-alpine
COPY docs/package.json /docs/package.json
WORKDIR /docs
RUN npm install

EXPOSE 8000
# Copy the entire documentation directory into the
# build context
COPY docs/ /docs/
COPY --from=schema-builder /build/schema.html /docs/build/schema.html
RUN ls -la build
CMD node_modules/.bin/gatsby develop -H 0.0.0.0
