from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.handlers import register_handlers
from app.core.lifecycle import lifespan
from app.core.middlewares import register_middlewares
from app.schemas.response import SuccessResponse


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
        debug=settings.DEBUG,
    )
    register_middlewares(app)
    register_handlers(app)
    app.include_router(api_router, prefix=settings.API_PREFIX)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    @app.get("/", tags=["root"])
    async def index():
        app_info = {
            "name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "debug": settings.DEBUG,
            "server_host": settings.SERVER_HOST,
            "server_port": settings.SERVER_PORT,
            "public_url": settings.PUBLIC_URL,
            "api_prefix": settings.API_PREFIX,
        }
        return SuccessResponse(data=app_info)

    return app


app = create_app()
