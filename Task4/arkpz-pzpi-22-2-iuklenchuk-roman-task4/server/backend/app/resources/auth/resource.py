import os
from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import User, get_db
from app.utils.email import send_email
from app.utils.verification import verify_password, hash_password, generate_random_password
from app.utils.auth import create_access_token, create_refresh_token, get_current_user, Authorization

from .schema import *


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

auth_router = APIRouter(prefix="/auth", tags=["auth"])


async def authenticate_user(username: str, password: str, db: AsyncSession):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        return None
    return UserInDB(username=user.username, email=user.email, password=user.password)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(
        User.email == user_create.email)
    existing_user_ = await db.execute(query)
    existing_user = existing_user_.first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(user_create.password)

    new_user = User(
        username=user_create.username,
        email=user_create.email,
        password=hashed_password,
        role=user_create.role,
        first_name=user_create.first_name,
        last_name=user_create.last_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully", "user": new_user}


@auth_router.post("/token", response_model=Token)
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post("/refresh-token", response_model=TokenWithRefreshToken)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(refresh_token, db)

    new_access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@auth_router.post("/restore-password")
async def restore_password(email: str,  db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )
    new_pass = generate_random_password()
    user.password = hash_password(new_pass)
    
    await db.commit()
    
    send_email.delay(user.id, f"Your new password: {new_pass}", "Password restoration")
    return {"msg": "Email with new password was sent to to you"}


@auth_router.post("/change-password", )
async def change_password(passwords: ChangePassword, user = Depends(Authorization()), db: AsyncSession = Depends(get_db)):
    if not verify_password(passwords.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
        
    user.password = hash_password(passwords.new_password)
    await db.commit()
    
    return {"msg": "Password changed successfully"}