# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project is working towards adherence to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).
We hope to arrive at full conformance for milestone `2.0.0`.

## `[unreleased]` - 2021-03-11

- Improved frontend and backend Docker images to have versions tied to the
  core application version (currently at `2.0.0.beta1`). This process will
  soon be integrated into an image building on release automation of some sort.
- Make Docker image builds use BuildKit and do more intelligent layer caching,
  potentially leading to significantly faster builds on fresh Sparrow installations.

### Frontend

Sparrow now has extensive editing capabilities on model admin pages.

- Linking to other data models can be easily done
  through frontend interactions.
  - On project admin page, samples can be directly linked to sessions
    through drag and drop.
- Forms for creating new project and sample models make data creation availble directly through the U.I.
- New researchers can be created from text field inputs.
- Any data model can be embargoed until a specific date or indefinitely
  (which currently means 3000 years).

Sparrow also integrates external resources into its editing capabilities to make filling in metadata more efficient.

- New publications can be searched for, by fuzzy text search or doi, and linked to projects and sessions through the U.I.
  - Search power provided by [xDD](https://xdd.wisc.edu/) and [crossref](https://www.crossref.org/).
  - Publications not found in search can also be manually added.
- Material metadata helpers use a vocabulary base from the sparrow db as well as [macrostrat](https://macrostrat.org/) while also leaving the ability for the user to create a new material.
- A prototype for sample geo entity can link a sample to its
  geologic context by choosing an entity name (i.e Apex Basalt), an entity type (i.e Formation), a
  reference datum (ie. top), and a reference distance (i.e 0.2 meters) (The sample was taken 0.2 meters
  from the top of the Apex Basalt Formation).

Frontend filtering of data is supported by robust API filtering
created in the backend. Data can be filtered by:

- Geographic location
- Date of session performed
- Embargo status
- Associated doi
- And any text fields such as name, material, description, etc

Other improvements to frontend include:

- Sample navigation from map sample marker as well as navigation to the map from the project and sample page maps.
- Enhanced model navigation through admin and catalog pages.
- Infinite scrolling lists on admin pages that is filterable and hideable to create a larger model view.
- Refined views overall on catalog and admin pages.

> NOTE:
> Some frontend editing may not be fully functional yet in their persisting to the database.
> Linking samples and sessions may create a new session or sample model instead of linking an already existing model.
> Newer releases will have these fixed as well as have new features including model tagging, ("needs work", "location wrong", etc) to quickly reference workflow, duplicate model consolidating and enhanced capabilities on the datasheet.

### Backend

Sparrow's API has recieved enhacements that include documentation, filtering and data posting.

The API documentation now has:

- More examples
- Basic information (version, license)
- Specific endpoint parameter information (more examples and descriptions specific to each model endpoint)

Sparrow's API now has even more extensive data filtering capabilities that are reflected in the frontend. Filters added include:

- `public`: Whether to search public or private data
- `date_range`: A range of dates that a linked session took place in.
- `doi_like`: Fuzzy search for a publication doi.
- `coordinates`: Pass 4 coordinates and recieve all data located with the geographic box.
- `geometry`: Pass a WKT geometry and get all data from within it.
- `like`: A general text field search.
- `age`: Search for a specific age.
- `ids`: Know the ids of the data models? Pass then in a list and get them all back.
  Some filters have extendable capabilities using database joins and data model schemas.

Sparrow now has a general all-purpose `PUT` and `POST` endpoint for each data model where edited and new models can be imported into the database through the API. The endpoints use model schemas for more robust handling.

> NOTE:
> There is still some debugging for the schema loading process, especially for editing data. Some complicated edge cases in editing nested models are still being debugged.

## `[2.0.0.beta1]` - 2021-03-01

This is the first release in the beta series for **Sparrow** version `2.0.0`.
The intent of the version 2 release series is to provide full support for
metadata management by labs — the focus of new features will then shift to
supporting integrations with community-level data systems and features.

### Database migrations

Sparrow now contains a database migrator that should ease future database
updates while maintaining flexibility. The migration process is multiphase:
first a diff between the current and ideal schema is created using
[Migra](https://databaseci.com/docs/migra). If no destructive changes will
occur, this migration is applied transparently; otherwise, manual migrations
are applied to manage destructive changes. A "dry run" is attempted on an
empty clone before applying changes to the real database.

In the future the migrator will ensure that
databases are properly backed up and gain better
tools for managing complex database changes and
migrations of Sparrow plugins, which can maintain
their own database schema extensions.

### Versioning

Sparrow can now be locked to a version or git commit. The
command-line applicaton now tests `SPARROW_VERSION` environment variable against either
a version specifier matching the [PEP 440](https://www.python.org/dev/peps/pep-0440/#version-specifiers)
specification, or a [git commit hash, tag, or other "commit-ish" revision](https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection).
For an unrestricted version, use `SPARROW_VERSION=HEAD` or don't set.

### A much quicker importer

The schema-based importer has been greatly sped up by bundling all changes
together and saving database transactions to the end of a schema unit of
work.

> Note:
> There is still a significant work to do on repeated imports of the same data, which
> should ideally be [_idempotent_](https://en.wikipedia.org/wiki/Idempotence) when data files have not changed. This will be addressed in future releases of the `2.0.0` beta series.

### Auto-building releases

GitHub Actions workflows for building command line application binaries are now active.
The application is bundled into a single executable with no dependencies (except for the
Docker engine) using PyInstaller. This workflow is run each time a tag is generated with
a name matching the pattern `v*.*.*` (a typical semantic versioning string, with optional
suffix). The output is binary files for both MacOS and Linux. The appropriate version
can be installed with the following one-line command:

```
curl -fsSL https://raw.githubusercontent.com/EarthCubeGeochron/Sparrow/HEAD/get-sparrow.sh | bash -s -
```

Downloadable releases are a **major deal** for
Sparrow's inter-lab usability. They remove
the need to download the Sparrow code repository,
install submodules, etc. in order to install the software. They pave the way for lighter-weight, integrated implementations of the system.

> Note:
> There are still some problems to be solved,
> like marking pre-releases appropriately and
> figuring out how a single application
> version works with how we manage versioning
> through different parts of the application.

### Command-line bundling

- The application can now be bundled using PyInstaller for packaged installation without
  pulling the Sparrow codebase. The CLI can be bundled using `make` and installed onto your
  path using `make install`.
- `make install` does not request elevated permissions within the script. You may have to run
  `sudo make install` to properly link the executable, depending on the configuration of your
  system.

### Other command-line enhancements

- Numerous command-line user-interface enhancements,
  including better organization of commands on the
  basic help page (`sparrow` called with no options)
- More consistent parsing of backend and
  container-orchestration commands.
- Improved division of commands into sections
- Refactored command-line application to a simpler
  Python-based framework for loading environment variables.

### Testing enhancements

Sparrow's test suite (runnable with `sparrow test`)
now includes 72 tests that check all aspects of the
application's core including data import and export

### Backend application changes

- Fully transitioned Sparrow's core to a [Starlette](https://www.starlette.io) server backend.
  This is a fairly major breaking change that requires plugins that extend the API to be updated.
- Sparrow plugins can now record compatible versions of Sparrow using the `sparrow_version` property.
  If an incompatible plugin is loaded, an error (for core plugins) or a warning will be generated.
- Added Visual Studio Code language server support within Sparrow's backend Docker container.

#### Internal API changes

- Transitioned hook `api-initialized` to `api-v1-initialized`.
- Created `add-routes` hook.
- Moved from `uvicorn` (dev) + `gunicorn` (production) to `hypercorn` for ASGI serving.

#### Authentication backend

- Replaced `/api/v1/auth` authentication API based on `flask_jwt_extended` with a more
  flexible `/api/v2/auth` endpoint utilizing [Starlette's `AuthenticationMiddleware`](https://www.starlette.io/authentication/)
- Added a suite of tests for the new authentication backend

### Frontend

- Excel-like data sheet with drag copy and paste
  features, for use when editing sample metadata.
- Map now has interactive markers with tooltips and popovers
- Sample's popovers contain links to the respective sample page
- Map has superclusters to increase loading performance
- Map has several default map styles that can be toggled (including macrostrat's geologic map)

> Note: more frontend changes to enable editing
> features are coming in later versions in the
> `2.0.0` series.

## `[1.6.0]` - 2020-09-10

- Moved database migration scripts to Python and created a test fixture to
  centralize data management.
- Refactored command-line application to a simpler Python-based framework.
- Packaged tests into a `sparrow_test` package, and added robustness,
  including database transaction isolation between test classes.
- Bumped `sparrowdata/backend-base` Docker image to `v1.2` to include `uvloop`
  (enables high-performance asynchronous serving).
- Switched Sparrow's backend to "ASGI" (a fast, asynchronous server interface)
  and switched web server to `gunicorn` for robustness.
- Preliminary implementation of Sparrow's API v2, including autogenerated
  model-based routes, nested recall, and basic filtering.

## `[1.5.0]` - 2020-07-22

- Build in SSL (https) termination with Certbot certificate generation.
- Improved loading of environment variables on application startup
- Add a skeletal redesigned documentation website
- Major update of key [`@macrostrat/ui-components`][1]
  dependency to `v0.2.1`, and transition this module from a bundled submodule
  to a typical dependency.
- Improved CLI application install procedure using `make install-dev`
- Bugfixes: CORS, importing geometries (#37)
- **Deprecated:** `-f <compose-file-override>` signature for `SPARROW_COMPOSE_OVERRIDES`
  environment variable. Use [`docker-compose`'s colon-separated `COMPOSE_FILE` signature][2] instead.

[1]: https://github.com/UW-Macrostrat/ui-components
[2]: https://docs.docker.com/compose/reference/envvars/#compose_file

## `[1.4.0]` - 2020-06-12

- Added basic command-line tests to `sparrow test` command.
- `SPARROW_PATH` is now explicitly required in `sparrow-config.sh` for source builds.
- Bundle `docker-compose` version `1.26.0` into the `sparrow` wrapper command
  to solve version issues on Ubuntu and other platforms.

## `[1.3.0]` - 2020-06-07

- Added GitHub Actions continuous integration for Sparrow tests
- Added continuous integration and deployment of documentation website to sparrow-data.org
- Added documentation tests to `sparrow docs-test` command
- Simplify application loading
- "Decaffeinate" frontend application from Coffeescript to Typescript.
- Command-line interface is now based on Python instead of shell scripts.

## `[1.2.0]` - 2020-06-02

- Add a plugin for cloud data import
- A new interface for calling plugin functions from elsewhere in the application
- More efficient Javascript bundles for production application
- Added an improved data model and API for tracking geological samples. The core
  of this change is the `geo_entity` table and `sample_geo_entity` linking table.
- Bugfixes for import interface

## `[1.1.0]` - 2020-05-07

## `[1.0.0]` - 2019-09-19

## `[0.2.0]` - May 2019

- Initial data management views
- The configuration stack was changed in to be more straightforward.
