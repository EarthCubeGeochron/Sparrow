FROM node:14 AS base

RUN npm install -g npm@7 webpack webpack-cli lerna
WORKDIR /app

CMD npm run dev

FROM base AS frontend

COPY package.json /app
RUN lerna bootstrap --hoist
COPY ./ /app/
CMD webpack
