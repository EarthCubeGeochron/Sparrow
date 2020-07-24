# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project is working towards adherence to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).
We hope to arrive at full conformance for milestone `2.0.0`.

## [Unreleased] - 2020-06-12

### Changed

- Command-line interface is now based on Python instead of shell scripts.
- Added basic command-line tests to `sparrow test` command.
- `SPARROW_PATH` is now explicitly required in `sparrow-config.sh` for source builds.
- Bundle `docker-compose` version `1.26.0` into the `sparrow` wrapper command
  to solve version issues on Ubuntu and other platforms.

## [Unreleased] - 2020-07-24

## Changed

- Map now has interactive markers with tooltips and popovers
- Sample's popovers contain links to the respective sample page
- Map has superclusters to increase loading performance
