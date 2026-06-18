"""
API Dependencies

Provides dependency injection for API routes.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db as db_session
from app.models.platform import PlatformUser
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError, NotFoundError


# Security scheme
security = HTTPBearer(auto_error=False)


async def get_db():
    """
    Dependency to get database session.
    
    Yields an async database session.
    """
    async for session in db_session():
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformUser:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current User instance
        
    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: Annotated[PlatformUser, Depends(get_current_user)],
) -> PlatformUser:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current User instance if active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[PlatformUser, Depends(get_current_active_user)],
) -> PlatformUser:
    """
    Dependency to get the current admin user.
    
    Args:
        current_user: Current active user
        
    Returns:
        Current User instance if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# Type aliases for cleaner route signatures
CurrentUser = Annotated[PlatformUser, Depends(get_current_user)]
ActiveUser = Annotated[PlatformUser, Depends(get_current_active_user)]
AdminUser = Annotated[PlatformUser, Depends(get_current_admin_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
