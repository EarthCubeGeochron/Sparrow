# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project is working towards adherence to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).
We hope to arrive at full conformance for milestone `2.0.0`.

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
There is still a significant work to do on repeated imports of the same data, which
should ideally be [*idempotent*](https://en.wikipedia.org/wiki/Idempotence) when data files have not changed. This will be addressed in future releases of the `2.0.0` beta series.


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
There are still some problems to be solved, 
like marking pre-releases appropriately and
figuring out how a single application
version works with how we manage versioning
through different parts of the application.

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

> Note: more frontend changes to enable editing
features are coming in later versions in the
`2.0.0` series.

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
