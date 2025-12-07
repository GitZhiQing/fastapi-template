import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    from app.core.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )
