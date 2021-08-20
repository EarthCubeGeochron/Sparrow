FROM node:14 AS base

# Yarn is already installed
RUN npm install -g webpack webpack-cli lerna
WORKDIR /app

CMD npm run dev

FROM base AS frontend

# This is annoying but I don't see a better alternative
COPY packages/schema-linker/package.json /app/packages/schema-linker/
COPY packages/sheet/package.json /app/packages/sheet/
COPY package.json .npmrc /app/
RUN yarn install
COPY ./ /app/
CMD webpack
