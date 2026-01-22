from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import ErrorTypeEnum
from app.core.exceptions import APIException
from app.schemas.response import Error, ErrorDetail, ErrorResponse


def register_handlers(app: FastAPI):
    """注册异常处理器"""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """处理自定义的业务异常"""
        return ORJSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=Error(type=exc.error_type, message=exc.message, details=exc.details)
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求参数校验失败异常"""
        details = [
            ErrorDetail(field=error["loc"][-1], message=error["msg"]) for error in exc.errors()
        ]
        return ORJSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=Error(
                    type=ErrorTypeEnum.DATA_VALIDATION,
                    message="Request validation error.",
                    details=details,
                )
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        """处理标准 HTTP 异常

        捕获所有由 FastAPI/Starlette 抛出的标准 HTTP 异常，
        并将其转换为统一的错误响应格式。
        """
        return ORJSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=Error(
                    type=ErrorTypeEnum.HTTP_EXCEPTION,
                    message=exc.detail,
                )
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(
        request: Request,
        exc: Exception,
    ):
        """处理所有未捕获的内部异常

        最后的防线，捕获所有意料之外的异常。
        """
        logger.exception(f"服务器内部错误: {exc}")

        return ORJSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=Error(
                    type=ErrorTypeEnum.INTERNA_SERVER_ERROR,
                    message="Internal server error.",
                )
            ).model_dump(),
        )
