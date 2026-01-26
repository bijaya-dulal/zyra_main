from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

from app.core.config import settings
from app.db import get_db
from app.models.users import User

# This tells FastAPI that the token comes from the "/login" endpoint
# It adds the "Authorize" button to your Swagger UI (/docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Decodes the JWT token and returns the current user.
    If token is invalid or user doesn't exist, raises 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the Token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # 2. Extract User ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except (JWTError, ValidationError):
        raise credentials_exception
        
    # 3. Fetch User from DB (To ensure they haven't been deleted/banned)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
         raise HTTPException(status_code=400, detail="Inactive user")
         
    return user

# Optional: Helper for Admin-only routes
async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="The user does not have enough privileges"
        )
    return current_user