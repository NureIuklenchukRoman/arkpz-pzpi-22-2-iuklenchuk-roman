import uuid
import random
from datetime import datetime as dt

from sqlalchemy import select, delete
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.utils.auth import Authorization
from app.database.models import Warehouse, Rental, RentalStatus, PremiumService, Message, Lock, UserRole

from .tasks import send_email
from .schemas import RentWarehouseSchema, WarehouseDetails


rent_router = APIRouter(prefix="/rent", tags=["rent"])


async def calculate_price(db, warehouse_data, price):
    start_date = warehouse_data.start_date
    end_date = warehouse_data.end_date
    days = (end_date - start_date).days
    price = days * price

    if warehouse_data.selected_services:
        for service in warehouse_data.selected_services:
            service_query = select(PremiumService).filter(
                PremiumService.id == service)
            service_result = await db.execute(service_query)
            service_ = service_result.scalar_one_or_none()
            price += service_.price

    return price


@rent_router.post("/{warehouse_id}")
async def rent_warehouse(warehouse_id: int,
                         warehouse_data: RentWarehouseSchema,
                         user=Depends(Authorization()),
                         db=Depends(get_db)):
    query = select(Warehouse).filter(Warehouse.id == warehouse_id)
    result = await db.execute(query)
    warehouse = result.scalar_one_or_none()

    if not warehouse or warehouse.is_blocked or warehouse.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found, deleted, or blocked by admins"
        )

    existing_rentals_query = select(Rental).filter(
        Rental.warehouse_id == warehouse_id,
        Rental.status == RentalStatus.RESERVED
    )
    existing_rentals_result = await db.execute(existing_rentals_query)
    existing_rentals = existing_rentals_result.scalars().all()

    for existing_rental in existing_rentals:
        if existing_rental.start_date <= warehouse_data.end_date <= existing_rental.end_date or \
                existing_rental.start_date <= warehouse_data.end_date <= existing_rental.end_date:
            raise HTTPException(
                status_code=400,
                detail="Warehouse is already reserved for this date"
            )

    rental = Rental(
        user_id=user.id,
        warehouse_id=warehouse_id,
        start_date=warehouse_data.start_date,
        end_date=warehouse_data.end_date,
        total_price=await calculate_price(db,
                                          warehouse_data, warehouse.price_per_day),
        selected_services=warehouse_data.selected_services,
        status=RentalStatus.RESERVED
    )
    db.add(rental)

    lock_qery = select(Lock).filter(Lock.warehouse_id == warehouse_id)
    lock_result = await db.execute(lock_qery)
    lock = lock_result.scalar_one_or_none()
    
    if not lock:
        raise HTTPException(
            status_code=404,
            detail="Lock warehouse not found"
        )

    lock.access_key = str(random.randint(10**9, 10**10 - 1))
    
    message_text = f"""Warehouse {warehouse.name} has been reserved successfully, 
                    from {warehouse_data.start_date} to {warehouse_data.end_date},
                    cost will be {rental.total_price},
                    wait for the owner to connect with you"""
                    
    message = Message(
        user_id=user.id,
        text=message_text,
    )
    db.add(message)
    await db.commit()
    
    send_email.delay(user.id, message_text, "Warehouse reservation")
    send_email.delay(warehouse.owned_by,
                     f"""Warehouse {warehouse.name} has been reserved by {user.email} from 
                     {warehouse_data.start_date} to {warehouse_data.end_date} for {rental.total_price} 
                     phone number: {user.phone}""", "Warehouse reservation")

    return {"message": "Warehouse reserved successfully"}


@rent_router.get("/{rent_id}", response_model=RentWarehouseSchema)
async def get_rent_details(rent_id: int, user=Depends(Authorization()), db=Depends(get_db)):
    query = select(Rental).filter(Rental.id == rent_id)
    result = await db.execute(query)
    rental = result.scalars().first()
    
    if not rental:
        raise HTTPException(
            status_code=404,
            detail="Rental not found"
        )
    return rental


@rent_router.get("/warehouse-rents/{warehouse_id}", response_model=list[RentWarehouseSchema])
async def get_warehouse_rents(warehouse_id: int, user=Depends(Authorization(allowed_roles=[UserRole.SELLER])), db=Depends(get_db)):
    warehouse = select(Warehouse).filter(Warehouse.id == warehouse_id)
    result = await db.execute(warehouse)
    warehouse = result.scalar_one_or_none()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    if warehouse.owned_by != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this warehouse rents"
        )

    query = select(Rental).filter(Rental.warehouse_id == warehouse_id)
    result = await db.execute(query)
    rentals = result.scalars().all()

    return rentals
