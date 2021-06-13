class SparrowError(Exception):
    """Base class for all sparrow-related errors"""

class SparrowSchemaError(SparrowError):
    ...

class DatabaseMappingError(SparrowError):
    """Raised when a problem occurs with finding a database model"""
