from fastapi import FastAPI
# from app.routers import warehouses
from app.database import Base, engine
from app.resources.auth.resource import auth_router
from app.resources.warehouses.resource import warehouse_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(warehouse_router)