FROM node:14 AS base

RUN npm install -g npm@7 webpack webpack-cli lerna
WORKDIR /app

CMD npm run dev

FROM base AS frontend

# This is annoying but I don't see a better alternative
COPY packages/schema-linker/package.json /app/packages/schema-linker/
COPY packages/sheet/package.json /app/packages/sheet/
COPY package.json lerna.json .npmrc /app/

RUN lerna bootstrap --hoist
COPY ./ /app/
CMD webpack
