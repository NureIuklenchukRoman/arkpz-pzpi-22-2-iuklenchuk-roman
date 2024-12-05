from fastapi import FastAPI
# from app.routers import warehouses
from app.database import Base, engine
from app.resources.auth.resource import router

app = FastAPI()

app.include_router(router)