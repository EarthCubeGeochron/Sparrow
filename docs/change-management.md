# Schema change management

We need to support some level of change management for database
schemas. The main schema definition should represent an atomic
way to stand up a database with the current version of the schema,
to maximize the ability to be used as a reference spec.

Migrations should be defined for each database change that,
run in order, define a mapping from one state to another of the database.

## Ingredients

- Versioned reference specification
- Migrations to map one version to another
- Way to test conformance of a realized database schema with its spec

## References

- https://www.depesz.com/2010/08/22/versioning/
