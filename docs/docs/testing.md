Sparrow has a robust testing framework for the database and API.
It is based on PyTest.

An example for testing a single piece of functionality:

`sparrow test --quick -k pychron --capture=no`

The `--quick` flag makes sure the database isn't torn down (leading to less dead time
for iterative testing).
