FROM node:11-alpine
COPY ./package.json /app/package.json
WORKDIR /app
RUN npm install

EXPOSE 8000
COPY . /app/
RUN node_modules/.bin/gatsby develop -H 0.0.0.0
