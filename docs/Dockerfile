# This actually is built from the base directory, NOT the docs directory.
# Simple dockerfile: https://github.com/vercel/next.js/blob/canary/examples/with-docker/Dockerfile

FROM node:14

WORKDIR /docs
# Copy files needed for installation
COPY ./docs/package*.json /docs/

# Install node modules
# Should use `npm ci` but there are errors
RUN npm install

COPY ./docs/ /docs/
COPY ./get-sparrow.sh /docs/public/

ENV NODE_ENV production

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]