from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routes import issues, auth, faq, notifications
from .routes import users
from .routes import admin
from .utils.error_handler import validation_exception_handler, http_exception_handler, generic_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

app = FastAPI(title='Civic Reporting Backend')

# Allow only the local frontend origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (each router sets its own prefix/tag)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(issues.router)
app.include_router(faq.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.get('/health')
def health():
    return {'ok': True}


# Custom exception handler for validation errors
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.app.main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), reload=True)
