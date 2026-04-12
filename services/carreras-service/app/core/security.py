from fastapi import HTTPException, Depends, Header
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "ADMIN"
    ESTUDIANTE = "ESTUDIANTE"


async def get_current_role(x_role: Optional[str] = Header(None)) -> str:
    """
    Obtener el rol actual del usuario desde el header x-role.
    
    En producción, esto se reemplazará con validación de JWT.
    Por ahora, solo verifica que el rol sea válido.
    """
    if not x_role:
        raise HTTPException(
            status_code=401,
            detail="No role provided. Use header: x-role: ADMIN or x-role: ESTUDIANTE"
        )
    
    # Validar que el rol sea válido
    try:
        role = RoleEnum(x_role.upper())
        return role.value
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Valid roles are: {', '.join([r.value for r in RoleEnum])}"
        )


def require_admin(role: str = Depends(get_current_role)) -> str:
    """Dependencia para requerir rol ADMIN"""
    if role != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to perform this action. Requires ADMIN role."
        )
    return role


def require_any_role(role: str = Depends(get_current_role)) -> str:
    """Dependencia para aceptar cualquier rol autenticado"""
    return role
