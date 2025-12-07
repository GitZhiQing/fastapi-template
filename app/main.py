from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.handlers import register_handlers
from app.core.lifecycle import lifespan
from app.core.middlewares import register_middlewares
from app.schemas.response import SuccessResponse


def create_app() -> FastAPI:
    from app.core.config import get_settings

    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
        debug=settings.DEBUG,
    )
    register_middlewares(app)  # 注册中间件
    register_handlers(app)  # 注册异常处理器

    @app.get("/", tags=["root"])
    async def index():
        app_info = {
            "name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "host": settings.PUBLIC_HOST,
            "port": settings.PUBLIC_PORT,
            "api_prefix": settings.API_PREFIX,
            "version": settings.APP_VERSION,
        }
        return SuccessResponse(data=app_info)

    app.include_router(api_router, prefix=settings.API_PREFIX)

    settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    return app


app = create_app()
