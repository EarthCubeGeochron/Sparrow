# sparrow.loader

The `sparrow.loader` module helps you prepare data for loading
into the Sparrow geochemistry database system.

When disconnected from a database, it can be used to check that
data is ready to be imported into a standard installation of
Sparrow.

If connected to a Sparrow installation's PostgreSQL database,
the module can be used to insert data into the appropriate tables.

## Key functions

- `validate_data(schema_name: str, data: dict)`  
  Checks data against a loader schema
- `show_loader_schemas(schema_name: str,  ..., nest_depth=0)`  
  Show the fields for one or several loader schemas.

## Installation

`pip install sparrow-loader`

Requires Python `>=3.9`