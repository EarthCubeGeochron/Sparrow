# EarthCube Lab Data Interface

This repository will soon hold software for managing the geochronology data
created by an individual laboratory. This software has the goal of managing
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

## Environment variables

`LABDATA_CONFIG`: Location of `.cfg` files containing data.
