FROM node:11-alpine

RUN npm install -g linklocal webpack webpack-cli
WORKDIR /app
COPY package.json /app
RUN npm install --unsafe-perm
COPY ./ /app/
CMD ["/app/run-docker"]
