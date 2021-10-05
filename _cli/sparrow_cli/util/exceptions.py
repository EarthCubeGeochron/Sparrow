class SparrowCommandError(Exception):
    def __init__(self, *args, details=None):
        super().__init__(*args)
        if isinstance(details, bytes):
            details = details.decode("utf-8")
        self.details = details
