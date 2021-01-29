import typing
from starlette.exceptions import HTTPException


class ValidationError(HTTPException):
    def __init__(
        self,
        detail: typing.Union[str, typing.Dict[str, typing.List[str]]],
        status_code: int = 400,
    ):
        super().__init__(status_code=status_code, detail=detail)


class SerializationError(HTTPException):
    def __init__(
        self,
        detail: typing.Union[None, str, typing.Dict[str, typing.List[str]]] = None,
        status_code: int = 500,
    ):
        super().__init__(status_code=status_code, detail=detail)
