from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional

# --- 1. SHARED PROPERTIES ---
# These are fields common to reading and writing
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    picture: Optional[str] = None # New: For Google Avatar URL

# --- 2. INPUT SCHEMAS (Client -> Server) ---

# For Standard Signup (Email + Password)
class UserCreate(UserBase):
    password: Optional[str] = None
    role: str = "student" # Default role

# For Standard Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    # For Standard Signup (Email + Password)
class UserUpdate(UserBase):
    password: str
    role: str = "student" # Default role

# --- 3. OUTPUT SCHEMAS (Server -> Client) ---
# This is what you send back to React/Mobile. 
# CRITICAL: Never include the 'password' here.

class UserOut(UserBase):
    id: str
    role: str
    provider: str      # 'google' or 'local' - helpful for Frontend UI logic
    is_active: bool
    
    class Config:
        # This tells Pydantic to read data even if it's an SQLAlchemy object
        from_attributes = True 

# --- 4. TOKEN SCHEMA ---
# The standard response after a successful login
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut # Optional: Sending user info along with token saves a frontend request