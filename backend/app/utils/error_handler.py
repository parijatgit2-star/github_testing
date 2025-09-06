from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles FastAPI request validation errors.

    This handler catches `RequestValidationError` exceptions and returns a
    JSON response with a 422 status code and a consistent error format.

    Args:
        request: The incoming request object.
        exc: The `RequestValidationError` instance.

    Returns:
        A `JSONResponse` with status 422 and the validation error message.
    """
    return JSONResponse(status_code=422, content={"error": str(exc)} )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handles FastAPI's `HTTPException`.

    This handler catches `HTTPException` and formats it into a JSON response
    with the corresponding status code and detail message.

    Args:
        request: The incoming request object.
        exc: The `HTTPException` instance.

    Returns:
        A `JSONResponse` with the exception's status code and detail.
    """
    detail = exc.detail if hasattr(exc, 'detail') else str(exc)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles any other unhandled exceptions.

    This is a catch-all handler to prevent internal server errors from
    leaking sensitive information. It returns a generic 500 error. In a
    production application, the actual exception should be logged.

    Args:
        request: The incoming request object.
        exc: The `Exception` instance.

    Returns:
        A `JSONResponse` with status 500 and the exception message.
    """
    # Log the exception in real app (omitted here). Return generic message.
    msg = str(exc)
    return JSONResponse(status_code=500, content={"error": msg})
