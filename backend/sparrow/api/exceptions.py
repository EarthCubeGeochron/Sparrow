import typing
from starlette.exceptions import HTTPException


class SparrowAPIError(HTTPException):
    def __init__(self, detail, status_code=400):
        super().__init__(status_code=status_code, detail=detail)


class ValidationError(HTTPException):
    def __init__(
        self,
        detail: typing.Union[str, typing.Dict[str, typing.List[str]]],
        status_code: int = 400,
    ):
        super().__init__(status_code=status_code, detail=detail)


class ApplicationError(HTTPException):
    def __init__(
        self,
        detail: typing.Union[None, str, typing.Dict[str, typing.List[str]]] = None,
        status_code: int = 500,
    ):
        super().__init__(status_code=status_code, detail=detail)


class SerializationError(ApplicationError):
    ...
