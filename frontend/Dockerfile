FROM node:11-alpine AS base

RUN npm install -g webpack webpack-cli
WORKDIR /app

CMD sh -c "npm install && webpack"

FROM base AS frontend

COPY package.json /app
RUN npm install --unsafe-perm
COPY ./ /app/
CMD webpack
