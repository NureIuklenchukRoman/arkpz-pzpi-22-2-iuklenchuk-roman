from fastapi import FastAPI

from app.resources.auth.resource import auth_router
from app.resources.rent.resource import rent_router
from app.resources.user.resource import user_router
from app.resources.locks.resource import locks_router
from app.resources.messages.resource import messages_router
from app.resources.warehouses.resource import warehouse_router
from app.resources.premium_services.resource import services_router
from app.resources.humidity.resource import humidity_router

app = FastAPI()

routers = [auth_router, warehouse_router, rent_router,
           user_router, services_router, locks_router, messages_router, humidity_router]

for router in routers:
    app.include_router(router, prefix="/api")

# from app.database.fill_db import create_test_data


# create_test_data()