from fastapi import FastAPI
# from app.routers import warehouses
from app.database import Base, engine
from app.resources.auth.resource import auth_router
from app.resources.warehouses.resource import warehouse_router
from app.resources.rent.resource import rent_router
from app.resources.user.resource import user_router
from app.resources.premium_services.resource import services_router
from app.resources.locks.resource import locks_router

app = FastAPI()

routers = [auth_router, warehouse_router, rent_router, user_router, services_router, locks_router]

for router in routers:
    app.include_router(router)
