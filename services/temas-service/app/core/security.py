from enum import Enum
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException

from app.core.config import get_settings


class RoleEnum(str, Enum):
    ADMIN = "admin"
    ESTUDIANTE = "estudiante"


def decode_token(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    return payload


def get_current_role(payload: dict[str, Any] = Depends(decode_token)) -> str:
    role = str(payload.get("rol", "")).lower()
    if role not in {RoleEnum.ADMIN.value, RoleEnum.ESTUDIANTE.value}:
        raise HTTPException(status_code=403, detail="Invalid role in token")
    return role


def get_current_user_id(payload: dict[str, Any] = Depends(decode_token)) -> str:
    user_id = payload.get("userId")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token missing userId claim")
    return str(user_id)


def require_admin(role: str = Depends(get_current_role)) -> str:
    if role != RoleEnum.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin role required")
    return role


def require_authenticated(role: str = Depends(get_current_role)) -> str:
    return role
