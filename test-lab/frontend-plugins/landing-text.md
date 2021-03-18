# Sparrow test lab

Welcome to a basic test lab for Sparrow! This "lab" holds two samples originating
with [**WiscAr**](https://wiscar-sparrow.geoscience.wisc.edu) at University of
Wisconsin. It serves as a demo of the basic structure of the application and in-development
metadata management tools.

The code for this test implementation is housed in [the Sparrow GitHub repository](https://github.com/EarthCubeGeochron/Sparrow/tree/HEAD/test-lab), and
a local version of the configuration can be created using the `sparrow create-test-lab`
command.

## Administration interface

This instance of the application is automatically set up with a user (normally, you would
run `sparrow create-user` to handle this process).

Username: **`Test`**  
Password: **`Test`**

## Database console

This version of the application comes bundled with [**a database console**](database/)
that provides access to the underlying PostGIS data store. This is notably insecure, but
it is valuable for testing and assessment.

If running locally, the `sparrow` database can also be accessed
at host `localhost`, port `54321`, using desktop database management software such as
[Postico](https://eggerapps.at/postico/) and [DataGrip](https://www.jetbrains.com/datagrip/).
This is configurable using the `SPARROW_DB_PORT` environment variable.
