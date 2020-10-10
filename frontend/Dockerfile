FROM node:11-alpine

RUN npm install -g webpack webpack-cli
WORKDIR /app
COPY package.json /app
RUN npm install --unsafe-perm
COPY ./ /app/
CMD webpack
