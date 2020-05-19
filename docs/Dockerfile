FROM node:11-alpine
COPY ./package.json /app/package.json
WORKDIR /app
RUN npm install

EXPOSE 3000
COPY . /app/
CMD node_modules/.bin/docusaurus start --host 0.0.0.0 --port 3000
