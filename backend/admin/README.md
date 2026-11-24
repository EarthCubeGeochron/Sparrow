# Sparrow administration

Commands that manage a Sparrow lab's database: its schema, users, pipelines and
tasks. They run wherever this package is installed, against the database named
by `SPARROW_DATABASE`, and are not part of the lab's running services.

Most people reach them through the `sparrow` command (`pip install
'sparrow-cli[admin]'`), which supplies the database of the active environment
and asks before a change to production:

```sh
sparrow --env production schema plan
sparrow --env production db update
sparrow --env production create-user
```

A lab's plugins add commands with the `setup-cli` hook, as before.
