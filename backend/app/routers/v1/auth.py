# app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from authlib.integrations.starlette_client import OAuth
from app.core.config import settings
from app.db import get_db
from app.models.users import User
# ✅ Updated to match our previous schema naming
from app.schemas.user_schemas import UserCreate, UserLogin, UserOut
from app.core.security import get_password_hash, verify_password, create_access_token
#from app.schemas.token_schema import Token # You might need to create this simple schema

router = APIRouter()

# --- 1. SETUP OAUTH ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- 2. GOOGLE ROUTES ---
@router.get("/google/login") # Changed path slightly for clarity
async def login_google(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Auth Failed: {str(e)}")

    user_info = token.get('userinfo')
    if not user_info:
         # Fallback if userinfo is not in token
         user_info = await oauth.google.userinfo(token=token)

    # Check existence
    result = await db.execute(select(User).where(User.email == user_info['email']))
    user = result.scalars().first()

    if not user:
        # Auto-Signup
        user = User(
            email=user_info['email'],
            full_name=user_info.get('name'),
            picture=user_info.get('picture'),
            provider="google",
            role="student",
            hashed_password=None 
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    access_token = create_access_token(subject=user.id, role=user.role)
    return {"access_token": access_token, "token_type": "bearer", "status": "Login Successful"}

# --- 3. LOCAL ROUTES ---
@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password safely
    hashed_pw = get_password_hash(user_in.password) if user_in.password else None

    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        role="student",
        provider="local"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalars().first()

    if not user or not user.hashed_password or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    return {"access_token": access_token, "token_type": "bearer"}