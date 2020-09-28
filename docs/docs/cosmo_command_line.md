### Command line functions for the Cosmo branch

```
Commands:
  config                  Print configuration of backend
  console                 Get a Python shell within the application
  create-user             Create an authorized user for the web frontend
  create-views            Recreate views only (without building rest of...
  import-earthchem        Import EarthChem vocabulary files
  init                    Initialize database schema (non-destructive)
  plugins                 Print a list of enabled plugins
  remove-analytical-data
  remove-audit-trail      Remove PGMemento audit trail
  serve                   Run a development WSGI server
  show-interface          Show the import interface for a database model.
  update-location-names   Update location names

Cosmogenic Nuclides Lab commands:
  import-data             Import cosmogenic nuclide XLSX data

Container management commands:
  compose                 Alias to docker-compose that respects sparrow config
  test                    Run sparrow's testing suite.
  shell                   Get a shell in a particular container
  psql                    Get a psql session to the database
  docs-up                 
  up                      Build containers, start, detach, and follow logs.
  db-graph                Graph database schema to dot format.
  build                   Build docker base images
  db-await                Utility that blocks until database is ready
  docs-test               
  monitor                 Run a monitor
  down                    Simple wrapper for docker-compose down
  printenv                Print sparrow environment variables to a file
  db-drop                 Drop the Sparrow database. DANGEROUS
  db-migration            Generate a changeset against the optimal database schema
  db-export               Export database to a binary pg_dump archive
  db-import               Import database from binary pg_dump archive
  exec                    Quick shortcut to docker-compose exec
  db-backup               Backup database to SPARROW_BACKUP_DIR
  status                  Get the status of the running Sparrow instance.
  kill                    Like sparrow down, but for people in a hurry.
  test-runtime            Run tests for Sparrow
  restart                 
  dev-reload              Reload web browser if app is in development mode
  ```
  
  