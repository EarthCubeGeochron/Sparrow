# This actually is built from the base directory, NOT the docs directory.
# Simple dockerfile: https://github.com/vercel/next.js/blob/canary/examples/with-docker/Dockerfile

FROM node:12-slim

WORKDIR /docs
# Copy files needed for installation
COPY docs/package.json /docs/package.json
#COPY docs/package-lock.json /docs/package-lock.json

# Install node modules
RUN npm ci 

COPY docs/ /docs/

ENV NODE_ENV production

EXPOSE 3000
