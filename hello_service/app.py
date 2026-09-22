"""Application factory.

`app` is the object Uvicorn imports. Tests build a fresh instance per case via
create_app so state does not leak between tests.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from hello_service.routes.items import router as items_router


def create_app() -> FastAPI:
    """Build the application. Side-effect free so tests can call it freely."""
    application = FastAPI(title="hello-service", version="0.3.1")
    application.include_router(items_router)

    @application.get("/healthz", include_in_schema=False)
    def healthz() -> dict:
        """Liveness probe. Always 200 as long as the process is up."""
        return {"status": "ok"}

    @application.get("/readyz", include_in_schema=False)
    def readyz() -> JSONResponse:
        """Readiness probe. Unlike healthz, a bad database makes this fail."""
        from hello_service.db import get_engine

        try:
            get_engine()
        except Exception:
            return JSONResponse({"status": "not ready"}, status_code=503)
        return JSONResponse({"status": "ready"})

    @application.exception_handler(ValueError)
    async def value_error_handler(request, exc) -> JSONResponse:
        """ValueError from a route means bad input, not a crash."""
        return JSONResponse({"detail": str(exc)}, status_code=400)

    return application


app = create_app()


def main() -> None:
    """Console-script entry point: hello-service."""
    import uvicorn

    uvicorn.run("hello_service.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
