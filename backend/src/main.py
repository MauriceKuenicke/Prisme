import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from .core.config import settings
from .api.routes import auth, consultants, blocks, links, profiles

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Note: Database tables are created via Alembic migrations

# Create FastAPI app
app = FastAPI(
    title="Prismé API",
    description="Consulting Profile Management API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(consultants.router, prefix="/api/v1")
app.include_router(blocks.router, prefix="/api/v1")
app.include_router(links.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "prisme-api"}


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope) -> Response:
        # Never rewrite API requests to index.html; keep proper 404 behavior.
        if path == "api" or path.startswith("api/"):
            return await super().get_response(path, scope)

        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise

            # If request is for an asset file (has extension), keep the 404.
            if "." in os.path.basename(path):
                raise

            # SPA history fallback for client-side routes (e.g. /admin/dashboard).
            return await super().get_response("index.html", scope)


# Mount static files (frontend build) in production
if STATIC_DIR.exists():
    app.mount("/", SPAStaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
