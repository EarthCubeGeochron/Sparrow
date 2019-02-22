# Sparrow

## An interface to lab data, supported by NSF EarthCube

**Sparrow** is software for managing the geochronology data
created by a laboratory. This software has the goal of managing
analytical data for indexing and public access.

The software is designed for flexibility and extensibility, so that it can
be tailored to the needs of individual analytical labs that manage a wide
variety of data. Currently, we are testing the software with Ar and detrital
zircon geochronology data.

This is both a software implementation and a specification of the default
interface that the "Lab Data Interface" will expose.

## Principles

- Federated
- Standardized basic schema
- Standardized web-facing API
- Flexible and extensible

## Modes of access

When data leaves an analytical lab, it is integrated into publications
and archived by authors. It is also archived by the lab for long-term storage.
We intend to provide several modes of data access to ease parts of this
process.

A project-centric web user interface, managed by the
lab and possibly also the researcher. We hope to eventually
support several interactions for managing the lifecycle
of analytical data:

- Link literature references to laboratory archival data
- Manage sample metadata (locations, sample names, etc.)
- Manage data embargos and public access
- Visualize data (e.g. step-heating plots, age spectra)
- Track measurement versions (e.g. new corrections)
- Download data (for authors' own analysis and archival purposes)

On the server, direct database access and a
command line interface will allow the lab to:

- Upload new and legacy data using customized scripts
- Apply new corrections without breaking
  links to published versions or raw data
- Run global checks for data integrity
- Back up the database

A web frontend will allow users outside the lab to

- Access data directly from the lab through an API for meta-analysis
- Browse a snapshot of the lab's publicly available data, possibly
  with data visualizations.
- Pull the lab's data into other endpoints, such as the Geochron
  and Macrostrat databases.

## Place within the lab

This software is designed to run on a standard virtualized
UNIX server with a minimum of setup and intervention, and outside
of the data analysis pipeline.
It will be able to accept data from a variety of data
management pipelines through simple import scripts. Generally,
these import scripts will be run on an in-lab machine with access
to the server. Data collection, storage, and analysis tools
such as [`PyChron`](https://github.com/NMGRL/PyChron)
sit immediately prior to this system in a typical lab's data production pipeline.

## Design

We want this to be software that can be used by many labs, so a
strong and flexible design is crucial. We envision an
extensible core with well-documented interfaces for pluggable
components. Key goals from a development perspective will
be a clear, concise, **well-documented** and extensible schema,
and a reasonably small and stable code footprint for the
core functionality, with clear "hooks" for lab specific
functionality.

Currently, we envision a technology stack consisting of

- Python-based backend (v3)
- `sqlalchemy` for database access
- `Flask` for web-application development
- `click` for command line
- PostgreSQL as the database backend (optionally configurable to other
  databases) with a configurable and extensible schema
- Managed with `git` with separate branches for analytical
  types and individual labs.
- Code and issues tracked on Github.
- Software packaged for virtualized servers, and potentially
  for lightweight, containerized (e.g. Docker) instances.

## Possible technologies for backend

- `migra` for PostgreSQL schema migrations?
- Command-line plugins can be enabled by `click-plugins`.

## Current limitations of the data model

- Publications are linked to individual projects, when a more granular
  level could be appropriate.

# Development

For development, Sparrow can be run locally or in a set of Docker
containers.

Clone this repository and fetch submodules:
```
git clone https://github.com/EarthCubeGeochron/Sparrow.git
cd Sparrow
git submodule update --install
```

Set the environment variable `LABDATA_SECRET_KEY` before developing.

In both local and containerized environments, the frontend and backend server
both run in development mode — changes to the code are compiled in real time
and should be available upon browser reload. This will be disabled in the
future with a `SPARROW_ENV=<development,production>` environment variable that
will default to `production` and disable development-focused capabilities for
performance and security.

## Local development

Development on your local machine can be easier than working with
a containerized version of the application. You must have several dependencies
installed:

- PostgreSQL v11/PostGIS (the database system)
- Python >= 3.7
- Node.js >= 8

It is recommended that you work in a Python virtual environment.

## Development with Docker

In its containerized form, the app can be installed easily
no matter what environment you are working in. This containerized
distribution strategy will allow easy deployment on whatever infrastructure
(local, cloud hosting, AWS/Azure, etc.) your lab uses to run the system.
The Docker toolchain stable and open-source.

First, [install Docker](https://docs.docker.com/install/)
using the instructions for your platform.

In the root directory of this repository, run `docker-compose up --build`. This
should spin up a database engine, frontend, backend, and gateway service
(details of each service can be found in the `docker-compose.yaml` file). If
the database hasn't been initialized already, it will be created for you. The management frontend
should now be accessible at `http://localhost:5002`, and the API at `http://localhost:5002/api`.

Note: the PostgreSQL database engine can be accessed from `localhost` at port
`54321` (user `postgres`). This is useful for schema introspection and data
management using local tools such as `psql` or
[Postico](https://eggerapps.at/postico/).

On navigating to the web interface for the first time, you will not be logged
in — indeed, no user will exist! To solve this, we need to create a username
and password. This can be accomplished by running `sparrow create-user` and
following the prompts. When you are running with Docker, the `sparrow` command
will not be accessible. We have provided a `sparrow-exec` command for this
purpose: simply run `bin/sparrow-exec create-user` and follow the prompts.
There should be a single row in the `user` table after running this command.

## Environment variables index

- `LABDATA_SECRET_KEY="very secret string"`: A secret key used for management
  of passwords. Set this in your **LOCAL** environment (it will be copied to
  the Docker runtime as needed). It is the only variable required to get up and
  running with a basic Dockerized version.
- `LABDATA_CONFIG="<path>"`: Location of `.cfg` files containing data.
- `LABDATA_CONFIG_JSON="<path>"`: Location of `.json` file containing frontend
  configuration. This can be manually generated, but is typically set to the
  output of `labdata config`. It is used when the frontend and backend are on
  isolated systems (i.e. when running using Docker).

