from os import environ

LAB_NAME="Test lab"
DATABASE="postgresql:///earthcube_labdata_test"

# We want to check most of our config into version control,
# but we should under no circumstances check in secret keys.
# Instead, we store it as an environment variable.
SECRET_KEY=environ.get("LABDATA_SECRET_KEY")
