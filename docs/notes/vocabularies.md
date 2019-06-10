# Data type mapping

An important thing to figure out is how different types
of data map onto the schema we are developing here. We use a
data hierarchy of `sample -> session -> analysis -> datum`

For example, **Boise State** uses a nested `sample -> aliquot -> fraction -> value` data
to represent data, with model ages represented as values at the the `aliquot` level.
This does not map straightforwardly to the schema we've designed, as model ages
do not link to an individual `fraction` but rather a collection of all the fractions.
As an interim solution, we will define an "`analysis`" that represents the model
age computed from a multi-zircon summary.
