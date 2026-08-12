FROM node:20 AS base

WORKDIR /app/

FROM base AS frontend

COPY package.json .

RUN corepack enable && \
    yarn set version 3.2.3 && \
    npm install -g 'nodemon@^2.0.0' 'webpack@^5.0.0' 'webpack-cli@^4.0.0'

# This is annoying but I don't see a better alternative
COPY packages/schema-linker/package.json /app/packages/schema-linker/
COPY packages/sheet/package.json /app/packages/sheet/

COPY yarn.lock .yarnrc.yml /app/
COPY .yarn/releases/*.cjs /app/.yarn/releases/
RUN yarn install --frozen-lockfile

COPY ./ /app/

RUN yarn install --frozen-lockfile

CMD yarn run start

