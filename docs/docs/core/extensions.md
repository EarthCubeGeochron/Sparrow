---
id: extensions
title: Extending the application
sidebar_label: Extensions
---

The `base-images/db-mysql-fdw` image is provided to build a
Sparrow-compatible PostGIS image with the MySQL foreign data wrapper extension (for connecting with external MySQL databases).
This functionality is not enabled by default because it adds ~700 Mb
to the installed size of Sparrow and will not be necessary for most
setups. However, it can be enabled with two steps: first, build the
appropriate Docker image with `sparrow build db-mysql-fdw`. Then
override the `db` portion of the `docker-compose.yaml` file with the
new image definition: 1., create an overrides file (e.g. `docker-compose.overrides.yaml` with the following contents:

```
version: "3.4"
services:
  db:
    image: sparrowdata/db-mysql-fdw:1.0
```

2. reference this overrides file with the `SPARROW_COMPOSE_OVERRIDES` environment variable in your config file, e.g.

```
SPARROW_COMPOSE_OVERRIDES=(<path>/<to>/docker-compose-overrides.yaml)
```

This will update the Sparrow configuration transparently to use the
new image in place of the default.

Once the image builds, you can run `CREATE EXTENSION mysql_fdw` in the
sparrow database, or add this command to your `SPARROW_INIT_SQL` file.
