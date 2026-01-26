from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 1. Setup Password Hashing
# "bcrypt" is the standard. 'deprecated="auto"' handles older hash formats if you ever migrate data.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a raw password against the stored hash.
    Used in: POST /auth/login
    """
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a secure hash from a raw password.
    Used in: POST /auth/signup
    """
    return pwd_context.hash(password)

# 2. Setup JWT Token Creation
def create_access_token(subject: Union[str, Any], role: str = "student") -> str:
    """
    Generates a JWT Access Token linked to a specific user and their role.
    
    Args:
        subject: The User ID (e.g., "user_12345")
        role: The user's permission level ('student', 'teacher', 'admin')
    
    Returns:
        str: The encoded JWT string
    """
    # Use timezone-aware UTC time (Best Practice)
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # The Token Payload
    to_encode = {
        "sub": str(subject),  # Subject (User ID)
        "role": role,         # Role is CRITICAL for your permission system
        "exp": expire,        # Expiration timestamp
        "iat": now,           # Issued At timestamp
        "type": "access"      # Token type
    }
    
    # Sign the token using the SECRET_KEY from your .env
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt