---
path: "/docs/cli"
---

# Command-line interface

**Sparrow** is administered using the `sparrow` command-line
interface. This command wraps application management, database management,`docker-compose` orchestration subcommands in a single executable, simplifying
basic management tasks.

```
Usage: sparrow [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config            Print configuration of backend
  create-user       Create an authorized user for the web frontend
  create-views      Recreate views only (without building rest of schema)
  import-earthchem  Import EarthChem vocabularies
  init              Initialize database schema (non-destructive)
  serve             Run a development WSGI server
  shell             Get a Python shell within the application

Docker orchestration commands:
  compose           Alias to docker-compose that respects sparrow config
  db-await          Utility that blocks until database is ready
  db-backup         Backup database to SPARROW_BACKUP_DIR
  db-export         Export database to a binary pg_dump archive
  db-import         Import database from binary pg_dump archive
  db-migration      Generate a changeset against the optimal database schema
  db-tunnel         Tunnel database connection to local port [default: 54321]
  dev-reload        Reload web browser if app is in development mode
  down              Simple wrapper for docker-compose down
  exec              Quick shortcut to docker-compose exec
  psql              Get a psql session to the database
  up                Build containers, start, detach, and follow logs.
```
