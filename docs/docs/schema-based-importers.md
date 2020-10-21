---
id: schema-imp
title: Schema-based importing
sidebar_label: Schemas and importing data
---

## What is a schema?

A schema is a formal formatted representation of data as defined in
the [Sparrow](https://sparrow-data.org/) database. Schema define the reproducible
structure that is entered into the database and allow for subsequent transformations
of data and connection to other databases.

Sparrow's _import schemas_ interface with
its _database schemas_ but are conceptually separate.
Sparrow's import infrastructure allows JSON with an
appropriate schema structure to be imported
using the API.

## Example schema from Sparrow

These schema examples are created using a simple API call.

## Using schema for importing data

Reorganization of data to fit the schema is key. There are many ways to do this, the easiest is likely a [Python](https://www.python.org/) script, although other languages like [R](https://www.r-project.org/) have also been used.

Example code for an R reformater used on data from the [WiscSIMS Lab](http://www.geology.wisc.edu/~wiscsims/) is available in this Github [file](https://github.com/thefallingduck/WiscSIMSDataExtractor/blob/7d6aae690397ac4fe2e9e2b774a80cc6f8a4facd/SparrowReformater.R).

The API has examples of schemas

<!-- Add MDX component for schema examples here -->

There is a command-line feature for seeing schema definitions:
`sparrow show-interface <name-of-interface>`.
This tells you how to assemble the correct JSON to import data.
