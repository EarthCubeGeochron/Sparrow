# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project is working towards adherence to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## `[2.4.1]` - 2022-06-23

- Fix bug with certbot configuration for certificates

## `[2.4.0]` - 2022-06-17

- Major update to frontend bundling to use [Yarn v3 and "Plug n' Play"](https://yarnpkg.com/features/pnp) dependency management
  instead of a `node_modules` folder. This allows a huge speedup in frontend bundling times. As part of this,
  the preferred minimum version of Node JS for frontend compilation has been increased to 16.
- Many bugfixes to the Task-management API system, and preparation for future improvements there.
- Added a `lab_id` field to the sample page
- Added basic integration tests (does the frontend build properly and get served by the gateway container?) to the 
  Sparrow CI process. These can be expanded and converted to Python in the future.

## `[2.3.1]` - 2022-06-07

- Fixed a bug with resolving the Python API server from the NGINX gateway
- Improved fault-tolerance of gateway server if API or frontend servers fail.
- Fix API healthcheck so it correctly reports health if the API is running

## `[2.3.0]` - 2022-06-06

- Added some nicer error pages to guide the user on application startup.
- Major updates to container orchestration to better differentiate `development` and `production` modes.
- Fix Webpack development server "hot reloading" for frontend code.
- Added a `sparrow dev printenv` command.
- Fixed https://github.com/EarthCubeGeochron/Sparrow/issues/287

## `[2.2.0]` - 2022-06-03

- Sparrow's caching mechanism for SQLAlchemy models was disabled, due to some
  problems with importers. It can be enabled on an opt-in basis using the
  `SPARROW_CACHE_DATABASE_MODELS` environment variable.
- More consistently drop caches using the `sparrow db drop-cache` command.

## `[2.1.4]` - 2022-06-03

- Fix a bug with bundling production instances
- Fix an issue with the `sparrow db import` command
- Add CLI commands to drop database caches (`sparrow db drop-cache` and `sparrow dev clear-cache` now both do this.)

## `[2.1.1]` - 2022-05-24

- **Command-line**: CLI returns success even when `docker`
  is not available, but warns the user.

## `[2.1.0]` - 2022-05-23

This version contains many fixes for data importing and some foundational improvements
to support future frontend updates.

### Command-line interface

- Add a `sparrow update` command that downloads/installs the most recent version of the Sparrow application.
- Fix `sparrow db import` command to be more reliable at reading database dump files
- Slightly relax the requirement to set `SPARROW_SECRET_KEY` (now this is only required for starting the application server).
- Improve bundling of command line application and upgrade PyInstaller.
- Improve documentation for server setup environment variables

### Data model and ingestion

- Add sample-researcher links
- Allow SQLAlchemy models to be passed to import schemas for all nested and related fields.
- Date importing fixes: allow Python `datetime` objects, `YYYY-MM-DD` dates, and `YYYY-MM-DD HH:MM:SS` date/times
  to be imported as well as ISO 8601 (`YYYY-MM-DDTHH:MM:SS`) date/times.
- Add tests for importing multiple instances of the same model
- Add tests for updating a module with new data

### Frontend

- Move to Webpack v5 for frontend bundling
- Simplify some framework code
- Vastly increase the performance of map areas with large numbers of data points

## `[2.0.0]` - 2022-03-27

This is the first non-beta release of the 2.0.0 series. It has most of the tools needed
to successfully track data within a single lab. Additional releases in this series will
focus on adding flexibility to this strong core, to track data from multiple labs or
the literature, and to improve documentation and usage instructions.

### Changes

- Added a `strict` model (disabled by default) to the importer. When enabled, this
  forces imports to fail when unknown fields are encountered.
- Added a model cache to the sparrow database (disabled by default)

## `[2.0.0.beta21]` - 2022-01-28

### Command-line interface

- Automatically read environment variables from `sparrow-config.overrides.sh` and `sparrow-secrets.sh`, if available.
- Add the concept of `messages` that the application can use to report common misconfigurations

### Data model

- Add a `sample.lab_id` column for use in internal lab tracking.
- Ensure that core analytical models (`sample`, `session`, and `analysis`) each have a `note` and `data`
  column for arbitrary text and JSON data, respectively.
- Add an `sample_attribute` linking model so that the `sample`, `session`, and `analysis` tables can all link to
  shared attributes.

## `[2.0.0.beta20]` - 2021-11-04

- Improved continuous integration scripts
- Fixed a bug with prestart scripts

## `[2.0.0.beta4]` - 2021-04-30

- Major fixes to the data sheet to prepare it for the future,
  especially column resizing and improved state management
- New multi-package repository organization for frontend code
- Better API error handling
- Improved speed for model-based APIs

## `[2.0.0.beta3]` - 2021-03-23

- Fixed a small but important database initialization [bug](https://github.com/EarthCubeGeochron/Sparrow/issues/76) that blocks new database setup for most lab setups
- **Frontend:** editing mode consistency across pages, partial refactor
- Remove unnecessary `metrics` database view (information is fetched using direct SQL querying instead).
## `[2.0.0.beta2]` - 2021-03-18
### Frontend

Sparrow now has extensive editing capabilities on model admin pages.

- Linking to other data models can be easily done
  through frontend interactions.
  For instance, on the project admin page, samples can be directly linked to sessions
  through drag and drop.
- Forms for creating new project and sample models make data creation availble directly through the U.I.
- New researchers can be created from text field inputs.
- Any data model can be embargoed until a specific date or indefinitely.

Sparrow also integrates external resources into its editing capabilities to make filling metadata more efficient.

- New publications can be searched for, by fuzzy text search or doi, and linked to projects and sessions through the U.I.
  - Search power provided by [xDD](https://xdd.wisc.edu/) and [CrossRef](https://www.crossref.org/).
  - Publications not found in search can also be manually added.
- Material metadata helpers use a vocabulary base from the Sparrow database
  and [Macrostrat](https://macrostrat.org/), while also leaving the ability for the user to create new materials.
- A prototype for sample geo entity can link a sample to its
  geologic context by choosing an entity name (e.g., *Apex Basalt*), an entity type (e.g., *Formation*), a
  reference datum (e.g., *top*), and a reference distance (e.g., *0.2 meters*), yielding the statement
  "*The sample was taken 0.2 meters from the top of the Apex Basalt Formation*".

New data filtering capabilities are supported by robust
API filtering (see backend changes). So far, data can be filtered by:

- Geographic location
- Date of session performed
- Embargo status
- Associated DOI
- Any text field (e.g., name, material, description, etc.)

Other improvements to frontend include

- Navigation from map (individual sample marker) to the sample page
- Navigation to the map from the project and sample page maps.
- Enhanced model navigation through admin and catalog pages.
- Infinite-scrolling lists sidebars on admin pages that are is filterable and hideable
- Refined views overall on catalog and admin pages.

> Note:
> Some frontend editing may not be fully functional yet in their persisting to the database.
> Linking samples and sessions may create a new session or sample model instead of linking an already existing model.
> Newer releases will have these fixed as well as have new features including model tagging, ("needs work", "location wrong", etc) to quickly reference workflow, duplicate model consolidating and enhanced capabilities on the datasheet.

### Backend

Sparrow's API has recieved enhacements that include documentation, filtering and data posting.

The API documentation now has:

- More examples
- Basic information (version, license)
- Specific endpoint parameter information (more examples and descriptions specific to each model endpoint)

Sparrow's API now has extensive data filtering capabilities that are reflected in the frontend. Filters added include:

- `public`: Whether to search public or private data
- `date_range`: A range of dates that a linked session took place in.
- `doi_like`: Fuzzy search for a publication doi.
- `coordinates`: Pass 4 coordinates and recieve all data located with the geographic box.
- `geometry`: Pass a WKT geometry and get all data from within it.
- `like`: A general text field search.
- `age`: Search for a specific age.
- `ids`: Know the ids of the data models? Pass then in a list and get them all back.
  Some filters have extendable capabilities using database joins and data model schemas.

Sparrow now has a general all-purpose `PUT` and `POST` endpoint for each data model where edited and
new models can be imported into the database through the API. The endpoints use model schemas for robust handling of edits.

> Note:
> There is still some debugging needed for the schema loading process, especially for editing data.
> Some complicated edge cases in editing nested models are still being debugged.

### Development process

- Frontend and backend Docker image versions are now tied to the
  core application version (currently at `2.0.0.beta1`). This process will
  soon be integrated into an "image building on release" automation of some sort.
- Docker image builds now use **BuildKit** for more intelligent layer caching,
  potentially leading to significantly faster builds on fresh Sparrow installations.
- Sparrow's default branch has changed from `master` to `main`. Running `git remote set-head origin -a`
  will update your remote `HEAD` reference to the correct version.

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
