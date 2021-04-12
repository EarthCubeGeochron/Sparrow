FROM node:14 AS base

RUN npm install -g npm@7 webpack webpack-cli
WORKDIR /app

CMD npm run dev

FROM base AS frontend

COPY package.json /app
RUN npm install --unsafe-perm
COPY ./ /app/
CMD webpack
