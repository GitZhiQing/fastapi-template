from typing import Any

from pydantic import BaseModel

from app.core.errors import ErrorTypeEnum


class PaginationInfo(BaseModel):
    """分页元信息"""

    page: int  # 当前页码
    size: int  # 每页数量
    total_items: int  # 总条目数
    total_pages: int  # 总页数


class PaginatedData[DataType](BaseModel):
    """分页数据容器"""

    items: list[DataType]
    pagination: PaginationInfo


class ErrorDetail(BaseModel):
    """错误详情"""

    field: str | None = None
    message: str


class Error(BaseModel):
    """错误主体"""

    type: ErrorTypeEnum
    message: str
    details: list[ErrorDetail] | None = None


class SuccessResponse[DataType](BaseModel):
    """成功响应"""

    success: bool = True
    data: DataType
    error: Error | None = None


class PaginatedResponse[DataType](BaseModel):
    """
    专用于分页的成功响应模型
    它是 SuccessResponse 的一个特化版本，其中 data 字段被固定为 PaginatedData[DataType]
    """

    success: bool = True
    data: PaginatedData[DataType]
    error: None = None


class ErrorResponse(BaseModel):
    """错误响应"""

    success: bool = False
    data: Any | None = None
    error: Error


type APIResponse[DataType] = SuccessResponse[DataType] | ErrorResponse
