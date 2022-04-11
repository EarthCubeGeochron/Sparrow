default_commands = {
    "config": {"help": "Print configuration of backend", "plugin": None},
    "create-user": {
        "help": "Create an authorized user for the web frontend",
        "plugin": None,
    },
    "create-views": {
        "help": "Recreate views only (without building rest of schema)",
        "plugin": None,
    },
    "db-migration": {"help": "Command to generate a basic migration.", "plugin": None},
    "db-update": {"help": "", "plugin": None},
    "import-earthchem": {
        "help": "Import EarthChem vocabulary files",
        "plugin": "earthchem-vocabulary",
    },
    "init": {"help": "Initialize database schema (non-destructive)", "plugin": None},
    "list-users": {"help": "", "plugin": None},
    "plugins": {"help": "Print a list of enabled plugins", "plugin": None},
    "remove-audit-trail": {
        "help": "Remove PGMemento audit trail",
        "plugin": "versioning",
    },
    "reset-password": {
        "help": "Reset the password for an existing user",
        "plugin": None,
    },
    "shell": {"help": "Get a Python shell within the application", "plugin": None},
    "show-interface": {
        "help": "Show the import interface for a database model.",
        "plugin": "schema-interface",
    },
    "tasks": {"help": "", "plugin": "task-manager"},
    "update-location-names": {
        "help": "Update location names",
        "plugin": "location-names",
    },
    "validate-data": {
        "help": "Try to import data into the database to see if errors are raised.",
        "plugin": "data-validation-cli",
    },
}
