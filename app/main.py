from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


app = FastAPI(
    title="Enterprise IT Operations Automation Platform",
    version="1.0.0",
    description="Production-oriented IT operations automation reference implementation.",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
