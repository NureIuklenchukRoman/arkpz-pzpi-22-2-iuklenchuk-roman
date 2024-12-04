from fastapi import FastAPI
# from app.routers import warehouses
from app.database import Base, engine


app = FastAPI()

# app.include_router(warehouses.router, prefix="/api")