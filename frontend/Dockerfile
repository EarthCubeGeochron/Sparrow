FROM node:11-alpine

RUN npm install -g linklocal webpack webpack-cli
WORKDIR /app
COPY . .
RUN npm install
CMD ["/app/run-docker"]
