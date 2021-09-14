class SparrowCommandError(Exception):
    def __init__(self, *args, details=None):
        super().__init__(*args)
        self.details = details
