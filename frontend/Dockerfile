FROM node:16 AS base

# Yarn is already installed
CMD yarn run dev:docker

FROM base AS frontend

WORKDIR /app/

COPY package.json .

RUN yarn set version berry && npm install -g nodemon webpack

# This is annoying but I don't see a better alternative
COPY packages/schema-linker/package.json /app/packages/schema-linker/
COPY packages/sheet/package.json /app/packages/sheet/

COPY yarn.lock .yarnrc.yml /app/
COPY .yarn/releases/*.cjs /app/.yarn/releases/
RUN yarn install --frozen-lockfile

COPY ./ /app/

CMD yarn run start

