import uvicorn
from src.config import settings
from src.logger import logger

def main():
    """Run the FastAPI application."""
    logger.info(f"Starting Market Analysis Agent API on {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()