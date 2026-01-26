from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import uuid4

from app.models.users import User
from app.schemas.user_schemas import UserCreate, UserUpdate

class AsyncUserService:  # ✅ Renamed from AsyncUploaderService

    @staticmethod
    async def list_users(db: AsyncSession, limit: int = 20, offset: int = 0):
        stmt = select(User).offset(offset).limit(limit)
        result = await db.scalars(stmt)
        return result.all()

    @staticmethod
    async def get_user(db: AsyncSession, user_id: str):
        stmt = select(User).where(User.id == user_id)
        user = await db.scalar(stmt)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate):
        # 1. Convert Pydantic data to a dictionary
        user_data = data.model_dump()
        
        # 2. Extract 'password' so it doesn't crash the model
        # The User model expects 'hashed_password', not 'password'
        raw_password = user_data.pop("password", None)
        
        # 3. Create the User instance
        new_user = User(
            id=str(uuid4()),
            hashed_password=raw_password, # ✅ Map it correctly here
            **user_data # Pass the rest (email, full_name, provider, etc.)
        )
        
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except Exception as e:
            await db.rollback()
            # Handle duplicate email errors gracefully
            if "unique constraint" in str(e).lower():
                 raise HTTPException(status_code=400, detail="Email already registered")
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, data: UserUpdate):
        user = await AsyncUserService.get_user(db, user_id)

        # Dynamic update
        for key, value in data.model_dump(exclude_unset=True).items():
            # If updating password, make sure to map it to hashed_password
            if key == "password":
                setattr(user, "hashed_password", value)
            else:
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str):
        user = await AsyncUserService.get_user(db, user_id)
        await db.delete(user)
        await db.commit()
        return True