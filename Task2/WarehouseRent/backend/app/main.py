from fastapi import FastAPI
# from app.routers import warehouses
from app.database import Base, engine
from app.resources.auth.resource import auth_router
from app.resources.warehouses.resource import warehouse_router
from app.resources.rent.resource import rent_router
from app.resources.user.resource import user_router

app = FastAPI()

routers = [auth_router, warehouse_router, rent_router, user_router]

for router in routers:
    app.include_router(router)
