---
id: local-dev
title: Local development
sidebar_label: Local development
---

Sometimes, it can be helpful to develop the web frontend
outside of the Docker container environment. This can be
especially helpful when you need to test in-development
versions of modules such as `@macrostrat/ui-components`
without fully packaging for NPM.

### Inserting local modules

Frontend modules being developed locally can be bundled into
Sparrow by mounting them into the frontend Docker image
at the `/app/_local_modules` directory. Modules installed
in this way will take precedence over globally-installed
Node modules. The `@macrostrat/ui-components` module,
which is foundational to the Sparrow web frontend,
can be bundled in by providing the `SPARROW_UI_COMPONENTS=<path>`
value to link the development directory.

### A fully local frontend

A locally-running frontend can be built by using the
`sparrow dev-local` command. This still
requires the Dockerized application to host the API.

:::note
Eventually, we will add a capability to run the
frontend completely detached from the API server, so
that Docker will not be required for frontend development.
:::
