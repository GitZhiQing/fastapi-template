from fastapi import HTTPException

from app.schemas.response import ErrorDetail

from .errors import ErrorTypeEnum


class APIException(HTTPException):
    """自定义 API 异常，用于统一错误响应格式"""

    def __init__(
        self,
        status_code: int,
        error_type: ErrorTypeEnum,
        message: str,
        details: list[ErrorDetail] | None = None,
    ):
        super().__init__(status_code=status_code)
        self.error_type = error_type
        self.message = message
        self.details = details


class UnauthorizedException(APIException):
    """未授权"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=401,
            error_type=ErrorTypeEnum.UNAUTHORIZED,
            message=message,
        )
        self.headers = {"WWW-Authenticate": "Bearer"}


class InvalidCredentialsException(APIException):
    """凭证无效，用户名或密码错误"""

    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(
            status_code=401,
            error_type=ErrorTypeEnum.INVALID_CREDENTIALS,
            message=message,
        )


class TokenInvalidException(APIException):
    """无效令牌，格式错误、签名失败、被篡改等"""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(
            status_code=401,
            error_type=ErrorTypeEnum.TOKEN_INVALID,
            message=message,
        )


class TokenExpiredException(APIException):
    """令牌已过期"""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            status_code=401,
            error_type=ErrorTypeEnum.TOKEN_EXPIRED,
            message=message,
        )


class PermissionDeniedException(APIException):
    """权限拒绝，用户尝试越权操作"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            status_code=403,
            error_type=ErrorTypeEnum.PERMISSION_DENIED,
            message=message,
        )


class UserDisabledException(APIException):
    """用户已被禁用"""

    def __init__(self, message: str = "User has been banned."):
        super().__init__(
            status_code=403,
            error_type=ErrorTypeEnum.USER_DISABLED,
            message=message,
        )


class UserNotVerifiedException(APIException):
    """用户未激活"""

    def __init__(self, message: str = "User is not verified."):
        super().__init__(
            status_code=403,
            error_type=ErrorTypeEnum.USER_NOT_VERIFIED,
            message=message,
        )


class NotFoundException(APIException):
    """未找到"""

    def __init__(self, message: str = "Item not found"):
        super().__init__(
            status_code=404,
            error_type=ErrorTypeEnum.ITEM_NOT_FOUND,
            message=message,
        )


class UsernameTakenException(APIException):
    def __init__(self, message: str = "Username is already taken"):
        super().__init__(
            status_code=409,
            error_type=ErrorTypeEnum.USERNAME_TAKEN,
            message=message,
        )


class EmailTakenException(APIException):
    def __init__(self, message: str = "Email is already taken"):
        super().__init__(
            status_code=409,
            error_type=ErrorTypeEnum.EMAIL_TAKEN,
            message=message,
        )


class PayloadTooLargeException(APIException):
    """请求体过大，上传的文件大小超出限制"""

    def __init__(self, message: str = "Payload too large"):
        super().__init__(
            status_code=413,
            error_type=ErrorTypeEnum.PAYLOAD_TOO_LARGE,
            message=message,
        )


class DataValidationException(APIException):
    """数据验证失败"""

    def __init__(
        self, message: str = "Data validation failed", details: list[ErrorDetail] | None = None
    ):
        super().__init__(
            status_code=422,
            error_type=ErrorTypeEnum.DATA_VALIDATION,
            message=message,
            details=details,
        )


class TooManyRequestsException(APIException):
    """请求过于频繁，如登录尝试次数过多"""

    def __init__(self, message: str = "Too many requests."):
        super().__init__(
            status_code=429,
            error_type=ErrorTypeEnum.TOO_MANY_REQUESTS,
            message=message,
        )


class InternalServerException(APIException):
    """服务器内部错误"""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=500,
            error_type=ErrorTypeEnum.INTERNA_SERVER_ERROR,
            message=message,
        )
