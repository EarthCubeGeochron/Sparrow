---
id: local-dev
title: Local Development
sidebar_label: Local Development
---

Sometimes, it can be helpful to develop the web frontend
outside of the Docker container environment. This can be
especially helpful when you need to test in-development
versions of modules such as `@macrostrat/ui-components`
without fully packaging for NPM.

A locally-running frontend can be built by using the
`sparrow dev-local` command. This still
requires the Dockerized application to host the API.

TODO: Eventually, we will add a capability to run the
frontend completely detached from the API server, so
that Docker will not be required for frontend development.
