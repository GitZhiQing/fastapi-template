import random
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import get_settings
from app.core.database import redis_client
from app.core.exceptions import PermissionDeniedException, UnauthorizedException
from app.models.user import User

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码哈希"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(sub: str, expires_delta: timedelta | None = None) -> str:
    """创建 Access Token"""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)  # 默认过期时间，15 分钟
    payload = {"sub": sub, "exp": expire, "type": "access"}
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return access_token


async def create_refresh_token(sub: str, expires_delta: timedelta | None = None) -> str:
    """创建 Refresh Token"""
    expires_delta = expires_delta if expires_delta else timedelta(days=7)  # 默认过期时间，7 天
    expire = datetime.now(UTC) + expires_delta
    refresh_token_id = str(uuid.uuid4())
    payload = {"sub": sub, "jti": refresh_token_id, "exp": expire, "type": "refresh"}
    refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    # 保存 refresh token 到 redis
    refresh_token_key = f"refresh_token:{sub}:{refresh_token_id}"
    await redis_client.setex(refresh_token_key, expires_delta, refresh_token)
    # 保存 refresh token ID 到 redis
    user_tokens_key = f"user_tokens:{sub}"
    await redis_client.sadd(user_tokens_key, refresh_token_id)
    return refresh_token


def verify_access_token(access_token: str) -> dict:
    """验证 JWT token 并返回 payload"""
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        sub: str = payload.get("sub")
        token_type: str = payload.get("type")
        if sub is None or token_type != "access":
            raise UnauthorizedException(msg="Access Token invalid")
        return payload
    except JWTError as e:
        raise UnauthorizedException(msg="Access Token invalid") from e


async def verify_refresh_token(refresh_token: str) -> dict:
    """验证 Refresh Token"""
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        sub: str = payload.get("sub")
        jti: str = payload.get("jti")
        token_type: str = payload.get("type")
        refresh_token_key = f"refresh_token:{sub}:{jti}"
        if sub is None or jti is None or token_type != "refresh":
            # Refresh Token 验证失败
            raise UnauthorizedException(msg="Refresh Token invalid")
        if not await redis_client.exists(refresh_token_key):
            # Refresh Token 已注销
            user_tokens_key = f"user_tokens:{sub}"
            await redis_client.srem(user_tokens_key, jti)
            raise UnauthorizedException(msg="Refresh Token revoked")
        return payload
    except ExpiredSignatureError as e:
        # Refresh Token 已过期
        user_tokens_key = f"user_tokens:{sub}"
        await redis_client.srem(user_tokens_key, jti)
        raise ExpiredSignatureError(msg="Refresh Token expired") from e
    except JWTError as e:
        # Refresh Token 验证失败
        raise UnauthorizedException(msg="Refresh Token invalid") from e


async def revoke_refresh_token(user_id: int, refresh_token_id: str) -> None:
    """撤销特定 Refresh Token"""
    refresh_token_key = f"refresh_token:{user_id}:{refresh_token_id}"
    await redis_client.delete(refresh_token_key)
    user_tokens_key = f"user_tokens:{user_id}"
    await redis_client.srem(user_tokens_key, refresh_token_id)


async def revoke_user_tokens(user_id: int) -> int:
    """注销用户的所有 Refresh Token"""
    user_tokens_key = f"user_tokens:{user_id}"
    token_ids = await redis_client.smembers(user_tokens_key)
    revoked_count = 0
    for token_id in token_ids:
        refresh_token_key = f"refresh_token:{user_id}:{token_id}"
        if await redis_client.exists(refresh_token_key):
            await redis_client.delete(refresh_token_key)
            revoked_count += 1
    await redis_client.delete(user_tokens_key)
    return revoked_count


def generate_security_password(length: int = 12) -> str:
    """
    生成安全且易于输入的密码

    特点:
    1. 避免容易混淆的字符 (0,O,o,1,l,I 等)
    2. 包含大小写字母、数字和特殊字符
    3. 字符分布均匀，提高安全性
    4. 长度适中，默认12位

    Args:
        length: 密码长度，默认12位

    Returns:
        str: 生成的安全密码
    """
    # 定义字符集，排除容易混淆的字符
    lowercase = "abcdefghijkmnpqrstuvwxyz"  # 排除 l, o
    uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # 排除 I, O
    digits = "23456789"  # 排除 0, 1
    special_chars = "!@#$%^&*_"  # 常用特殊字符

    # 确保密码包含各类字符至少一个
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars),
    ]

    # 所有字符集
    all_chars = lowercase + uppercase + digits + special_chars

    # 填充剩余长度
    for _ in range(length - 4):
        password.append(random.choice(all_chars))

    # 打乱顺序
    random.shuffle(password)

    return "".join(password)


def check_user_management_permission(current_user: User, target_user: User) -> None:
    """
    检查当前用户是否有权限管理目标用户，无权限时直接抛出异常

    权限规则:
    - 超级管理员(权限等级>=2)可以管理所有用户
    - 管理员(权限等级=1)可以管理普通用户和封禁用户(权限等级<=0)
    - 普通用户和封禁用户无管理权限

    Args:
        current_user: 当前用户
        target_user: 目标用户

    Raises:
        UnauthorizedException: 当没有权限管理时抛出
    """
    # 自己可以管理自己
    if current_user.id == target_user.id:
        return

    # 超级管理员可以管理所有用户
    if current_user.power.value >= 2:
        return

    # 管理员只能管理普通用户和封禁用户
    if current_user.power.value == 1 and target_user.power.value <= 0:
        return

    # 其他用户无管理权限
    raise PermissionDeniedException(msg="Insufficient permissions")
