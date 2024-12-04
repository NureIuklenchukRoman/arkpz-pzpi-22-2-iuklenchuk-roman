from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from ..base_model import Base
from sqlalchemy import select
from app.utils.verification import verify_password


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    email = Column(Text, unique=True)
    phone_number = Column(Text)
    password = Column(Text)

    @classmethod
    async def check_user_exists(cls, db, email):
        statement = select(cls).where(cls.email == email)
        result = await db.execute(statement)
        return result.scalar()

    @classmethod
    async def create(cls, db, user: dict):
        instance = cls(**user)
        await instance.save(db)
        return instance
    
    @classmethod
    async def authenticate(cls, db, email, password):
        statement = select(cls).where(cls.email == email)
        result = await db.execute(statement)
        user = result.scalar()
        if user is not None and verify_password(password, user.password):
            return user
        return None
    
    @classmethod
    async def update_user(cls, db, user):
        statement = select(cls).where(cls.email == user["email"])
        result = await db.execute(statement)
        user_instance = result.scalar()
        for key, value in user.items():
            setattr(user_instance, key, value)
        await user_instance.save(db)
        return user_instance
