# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project is working towards adherence to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).
We hope to arrive at full conformance for milestone `2.0.0`.

## [Unreleased] - 2020-08-31

- Refactored command-line application to a simpler python-based framework.
- Packaged tests into a `sparrow_test` package.

## [Unreleased] - 2020-07-24

### Changed

- More robust testing framework, including database transaction isolation between
  test classes.
- Bumped `sparrowdata/backend-base` Docker image to `v1.2` to include `uvloop`
  (enables high-performance asynchronous serving).
- Switched Sparrow's backend to "ASGI" (a fast, asynchronous server interface)
  and switched web server to `gunicorn` for robustness.

## [1.5.0] - 2020-07-22

### Changed

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

## [1.4.0] - 2020-06-12

### Changed

- Added basic command-line tests to `sparrow test` command.
- `SPARROW_PATH` is now explicitly required in `sparrow-config.sh` for source builds.
- Bundle `docker-compose` version `1.26.0` into the `sparrow` wrapper command
  to solve version issues on Ubuntu and other platforms.

## [1.3.0] - 2020-06-07

### Changes

- Added GitHub Actions continuous integration for Sparrow tests
- Added continuous integration and deployment of documentation website to sparrow-data.org
- Added documentation tests to `sparrow docs-test` command
- Simplify application loading
- "Decaffeinate" frontend application from Coffeescript to Typescript.
- Command-line interface is now based on Python instead of shell scripts.

## [1.2.0] - 2020-06-02

### Changes

- Add a plugin for cloud data import
- A new interface for calling plugin functions from elsewhere in the application
- More efficient Javascript bundles for production application
- Added an improved data model and API for tracking geological samples. The core
  of this change is the `geo_entity` table and `sample_geo_entity` linking table.
- Bugfixes for import interface

## [1.1.0] - 2020-05-07

## [1.0.0] - 2019-09-19

## [0.2.0] - May 2019

- Initial data management views
- The configuration stack was changed in to be more straightforward.
