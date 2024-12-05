from fastapi import Form
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
from sqlalchemy.orm import Session
# Make sure you import your actual SQLAlchemy User model and get_db from your database module
from app.database import User, get_db
from sqlalchemy.future import select
# Constants
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
router = APIRouter()


class UserSchema(BaseModel):
    name: str
    email: str | None = None


class UserInDB(UserSchema):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    name: str | None = None


class UserCreate(BaseModel):
    name: str
    password: str
    email: str | None = None


class TokenWithRefreshToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class OAuth2PasswordRequestFormCustom:
    def __init__(self, name: str = Form(...), password: str = Form(...)):
        self.name = name
        self.password = password


# Helper functions
REFRESH_TOKEN_EXPIRE_MINUTES = 1440  # 1 day


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def authenticate_user(name: str, password: str, db: Session):
    query = select(User).filter(User.name == name)
    result = await db.execute(query)  # Execute query asynchronously
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        return None
    return UserInDB(name=user.name, email=user.email, password=user.password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + \
        (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
        token_data = TokenData(name=name)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.JWTError:
        raise credentials_exception
    query = select(User).filter(User.name == token_data.name)
    existing_user_ = await db.execute(query)
    user = existing_user_.first()
    if user is None:
        raise credentials_exception
    return User(**user)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    query = select(User).filter(
        User.email == user_create.email)
    existing_user_ = await db.execute(query)
    existing_user = existing_user_.first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password
    hashed_password = hash_password(user_create.password)

    # Create the user in the database
    new_user = User(
        name=user_create.name,
        email=user_create.email,
        password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully", "user": new_user}




@router.post("/token", response_model=Token)
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestFormCustom = Depends()):
    print(f"\033[31m{form_data}\033[0m")

    user = await authenticate_user(form_data.name, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.name},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.name},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=TokenWithRefreshToken)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the refresh token to get the user information (ensure the token is valid)
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
        token_data = TokenData(name=name)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except jwt.JWTError:
        raise credentials_exception

    # Check if the user exists in the database using the token's information
    query = select(User).filter(User.name == token_data.name)
    existing_user_ = await db.execute(query)
    user = existing_user_.first()
    if user is None:
        raise credentials_exception

    # Create new access token and refresh token
    new_access_token = create_access_token(data={"sub": user.name})
    new_refresh_token = create_refresh_token(data={"sub": user.name})

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
