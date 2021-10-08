---
id: server-configuration
title: Server configuration
sidebar_label: Server configuration
---

Sparrow is configured using environment variables. Here are a few of the most
important ones:

- `SPARROW_SECRET_KEY="very secret string"`: A secret key used for management
  of passwords. Set this in your **LOCAL** environment (it will be copied to
  the Docker runtime as needed). It is the only variable required to run a basic test application.
- `SPARROW_BACKEND_CONFIG="<path>"`: Location of `.cfg` files containing data.
- The frontend is confugured using the variables `SPARROW_SITE_CONTENT`
  and `SPARROW_BASE_URL`. These values replace the former function of the `SPARROW_CONFIG_JSON` file.
- The `SPARROW_ENV=<development,production>` environment variable defaults to
  `production`, which disable development-focused features such
  as live code reloading and sourcemaps for performance and security.

:::note
More detailed configurations can be set by directly
using [docker-compose environment variables](https://docs.docker.com/compose/reference/envvars/).
:::
