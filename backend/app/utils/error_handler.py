from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a consistent JSON error for request validation errors."""
    return JSONResponse(status_code=422, content={"error": str(exc)} )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Format FastAPI HTTPException into consistent JSON structure."""
    detail = exc.detail if hasattr(exc, 'detail') else str(exc)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions. Avoid exposing internals."""
    # Log the exception in real app (omitted here). Return generic message.
    msg = str(exc)
    return JSONResponse(status_code=500, content={"error": msg})
