---
id: command-line-interface
title: Command-line interface
sidebar_label: Command-line interface
---

**Sparrow** is administered using the `sparrow` command-line
interface. This command wraps application management,
database management, and `docker-compose` orchestration subcommands in a
single executable, simplifying basic management tasks.

```
Usage: sparrow [options] <command> [args]...

No configuration file found
Lab:

Command groups:
  db                      Manage the sparrow database
  test                    Run sparrow's test suite
  docs                    Manage sparrow's documentation
  dev                     Helper commands for development

Backend:
  config                  Print configuration of backend
  create-user             Create an authorized user for the web...
  create-views            Recreate views only (without building rest of...
  db-migration
  import-earthchem        Import EarthChem vocabulary files
  import-pychron          Import PyChron Interpreted Age files.
  init                    Initialize database schema (non-destructive)
  plugins                 Print a list of enabled plugins
  remove-analytical-data
  remove-audit-trail      Remove PGMemento audit trail
  shell                   Get a Python shell within the application
  show-interface          Show the import interface for a database...
  update-location-names   Update location names

Container management:
  compose                 Alias to docker-compose that respects
                          sparrow config

  build                   Build Sparrow Docker images
  container-id
  create-test-lab         Create a configuration directory for a test...
  logs
  shell                   Get an iPython or container shell
  up                      Bring up the application and start logs
  psql                    Get a psql session to the database
  monitor                 Run a monitor
  down                    Simple wrapper for docker-compose down
  printenv                Print sparrow environment variables to a
                          file

  exec                    Quick shortcut to docker-compose exec
  status                  Get the status of the running Sparrow instance.
  kill                    Like sparrow down, but for people in a
                          hurry.

  test-runtime            Run tests for Sparrow
  restart
```
