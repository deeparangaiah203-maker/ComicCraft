from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    settings.ensure_directories()

    yield


app = FastAPI(
    title="ComicCraft",
    description=(
        "AI Comic Story Creator using Gemini "
        "and Hugging Face image generation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(settings.static_dir)),
    name="static",
)


# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

app.include_router(router)


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.get(
    "/health",
    tags=["system"],
)
async def health():
    return {
        "status": "ok",
        "mock_mode": settings.mock_mode,
    }