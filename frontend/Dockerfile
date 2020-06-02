FROM node:11-alpine

RUN npm install -g linklocal webpack webpack-cli
WORKDIR /app
COPY package.json /app
COPY run-docker /app
CMD ["/app/run-docker"]
