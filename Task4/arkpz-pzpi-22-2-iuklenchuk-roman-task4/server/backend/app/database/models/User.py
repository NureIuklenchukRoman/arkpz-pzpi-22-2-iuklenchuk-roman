from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, Enum
from ..base_model import Base
from sqlalchemy import select
from app.utils.verification import verify_password
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

class UserRole(PyEnum):
    ADMIN = "admin"
    SELLER = "seller"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    
    username = Column(Text)
    last_name = Column(Text)
    first_name = Column(Text)
    
    email = Column(Text, unique=True)
    phone = Column(Text)
    
    password = Column(Text)
    
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    is_blocked = Column(Boolean, default=False)
    
    rentals = relationship("Rental", back_populates="user")
    messages = relationship("Message", back_populates="user") 
    warehouses = relationship("Warehouse", back_populates="owner")
    
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
    async def update_user(cls, db, user):
        statement = select(cls).where(cls.email == user["email"])
        result = await db.execute(statement)
        user_instance = result.scalar()
        for key, value in user.items():
            setattr(user_instance, key, value)
        await user_instance.save(db)
        return user_instance
