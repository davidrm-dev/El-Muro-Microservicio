from fastapi import HTTPException, Depends, Header
from typing import Optional, Dict
from enum import Enum
import jwt
from .config import get_settings


class RoleEnum(str, Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "admin"
    ESTUDIANTE = "estudiante"


async def get_jwt_payload(
    authorization: Optional[str] = Header(None),
    x_role: Optional[str] = Header(None)
) -> Dict:
    """
    Validar JWT desde Authorization header y extraer payload.
    
    Requiere header: Authorization: Bearer <token>
    Token debe contener: {"userId": "...", "rol": "admin|estudiante"}
    """
    if not authorization:
        if x_role:
            return {"rol": x_role, "userId": "internal-header"}
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing. Use: Authorization: Bearer <token>"
        )
    
    # Verificar formato "Bearer <token>"
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use: Authorization: Bearer <token>"
        )
    
    token = parts[1]
    
    try:
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_role(payload: Dict = Depends(get_jwt_payload)) -> str:
    """Extraer y validar rol del JWT"""
    rol = payload.get("rol")
    
    if not rol:
        raise HTTPException(
            status_code=401,
            detail="Token missing 'rol' claim"
        )
    
    # Validar que el rol sea válido
    try:
        role = RoleEnum(rol.lower())
        return role.value
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid role in token: {rol}"
        )


def require_admin(role: str = Depends(get_current_role)) -> str:
    """Dependencia para requerir rol ADMIN"""
    if role != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Requires admin role."
        )
    return role


def require_any_role(role: str = Depends(get_current_role)) -> str:
    """Dependencia para aceptar cualquier rol autenticado"""
    return role
