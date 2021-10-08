An installation of Sparrow can have arbitrary views and tables added as plugins.
This is useful for adding lab-specific data and more convenient representations
of particular data types.

Plugins are Python classes that inherit from `sparrow.plugins.SparrowPlugin`
and implement one or more "hooks" to interact with the Sparrow application.

Plugins can be added in `sparrow-config.sh` by pointing an environment variable
to a [Python module that exports plugins](https://github.com/EarthCubeGeochron/Sparrow-LaserChron/tree/master/plugins)
(a directory with an `__init__.py` file containing references to the installed plugins):
```
export SPARROW_PLUGIN_DIR=plugins
```

[The `InitSQLPlugin`](https://github.com/EarthCubeGeochron/Sparrow/blob/master/backend/core_plugins/init_sql.py),
which is part of Sparrow core, is an example of a simple plugin that implements
the `on_core_tables_initialized` function to respond to the 'core-tables-initialized' hook.
This plugin (available in Sparrow core by default) allows startup SQL to be
initialized from a directory full of `*.sql` files. This plugin is enabled by adding
```
export SPARROW_INIT_SQL=dir-of-files
```
to `sparrow.sh`. If your plugin only needs to create views and tables on the database,
using this built-in capability is the most straightforward approach.
