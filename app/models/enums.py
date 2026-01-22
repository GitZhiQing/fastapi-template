from enum import IntEnum


class PowerEnum(IntEnum):
    """用户权限枚举"""

    BANNED = -1  # 封禁用户
    USER = 0  # 普通用户
    ADMIN = 1  # 管理员
    SUPER_ADMIN = 2  # 超级管理员
