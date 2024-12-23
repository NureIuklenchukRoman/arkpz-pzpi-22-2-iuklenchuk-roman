from sqlalchemy import select
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.database.models import Warehouse, Lock, UserRole
from app.utils.auth import Authorization, check_if_user_blocked
from app.utils.email import send_email
from .schemas import HumiditySchema


humidity_router = APIRouter(prefix="/humidity", tags=["humidity"])

@humidity_router.post("/{lock_id}")
async def notify_humidity(lock_id: int, humidity: HumiditySchema, db=Depends(get_db)):
    lock = await db.execute(select(Lock).filter(Lock.id == lock_id))
    lock = lock.scalar_one_or_none()
    warehouse = await db.execute(select(Warehouse).filter(Warehouse.id == lock.warehouse_id))
    warehouse = warehouse.scalar_one_or_none()
    send_email(warehouse.owned_by, humidity.value, "Humidity")
    return JSONResponse(content={"status": 1, "message": "Email sent successfully"})