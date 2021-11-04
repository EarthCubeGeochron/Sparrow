---
id: local-development
title: Local development
sidebar_label: Local development
---

## Frontend web application

Sometimes, it can be helpful to develop the web frontend
outside of the Docker container environment. This can be
especially helpful when you need to test in-development
versions of modules such as `@macrostrat/ui-components`
without fully packaging for NPM.

### A fully local frontend

A locally-running frontend can be built by using the
`sparrow dev-local` command. This still
requires the Dockerized application to host the API.

:::note
Eventually, we will add a capability to run the
frontend completely detached from the API server, so
that Docker will not be required for frontend development.
:::

## Core application

In certain situations, development on your local machine can be easier than
working with a containerized version of the application. However, configuration
bugs will be more likely, as this setup is not tested. **We do not recommend this approach.**

You must have several dependencies installed:

- PostgreSQL v11/PostGIS (the database system)
- Python >= 3.8
- Node.js~> 11

Working in a Python virtual environment is recommended.

When developing locally, the `sparrow-config.sh` file is not used, and the
frontend and backend must be configured directly. Orchestration and database
management commands from the `sparrow` command-line interface
are also unavailable; these could be implemented separately from the
Docker versions of the commands if there is demand.

## Debugger Tools

Several command line commands can help with python debugging.

`sparrow shell` will put you into an iPython shell and you can access the `Database` class and it's methods through `db`. Similarly you can access `App` through `app`.

When running python tests `--help` gives a short list while `app --help` gives a longer list of help.
Some helpful commands:

- `sparrow test -k test-name` : this command lets you run only a specific test given by the test name at the end of the line.
- `sparrow test --pdb` opens a python debugger at the point of the test failure to allow for easy debugging.
- `sparrow test --psql` opens a postgresSQL command line that you can run SQL commands on the test database that was created during tests
- `sparrow test --quick`

:::note
During testing the database schema is build everytime but the database is emtpy. If you want to test on real data you need to preload data at the beginning for your test using a method like `db.load_data()`.
:::
