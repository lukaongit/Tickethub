from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import logging
from contextlib import asynccontextmanager

from .routes import router
from .services import cleanup_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TicketHub service")
    yield
    logger.info("Shutting down TicketHub service")
    await cleanup_service()


app = FastAPI(
    title="TicketHub",
    description="Middleware REST service for support ticket management",
    version="1.0.0",
    lifespan=lifespan
)

# Include the ticket routes
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TicketHub"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
