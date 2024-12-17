from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy import select, delete
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.utils.auth import Authorization
from app.database.models import Warehouse, Rental, RentalStatus, PremiumService, Message

from .schemas import RentWarehouseSchema, WarehouseDetails


rent_router = APIRouter(prefix="/rent", tags=["rent"])


async def calculate_price(db, warehouse_data, price):
    start_date = warehouse_data.start_date
    end_date = warehouse_data.end_date
    days = (start_date - end_date).days
    price = days * price
    
    if warehouse_data.selected_services:
        for service in warehouse_data.selected_services:
            service_query = select(PremiumService).filter(PremiumService.id == service)
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

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
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
        total_price= await calculate_price(db,
            warehouse_data, warehouse.price_per_day),
        selected_services=warehouse_data.selected_services,
        status=RentalStatus.RESERVED
    )
    db.add(rental)
    
    message = Message(
        user_id=user.id,
        text=f"Your warehouse has been reserved successfully",
    )
    db.add(message)
    await db.commit()

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

# @rent_router.get("/warehouse-rents/{warehouse_id}", response_model=list[RentWarehouseSchema])
# async def get_warehouse_rents(warehouse_id: int, user=Depends(Authorization()), db=Depends(get_db)):
#     warehouse = select(Warehouse).filter(Warehouse.id == warehouse_id)
#     result = await db.execute(warehouse)
#     warehouse = result.scalar_one_or_none()
    
#     if not warehouse:
#         raise HTTPException(
#             status_code=404,
#             detail="Warehouse not found"
#         )
        
#     if warehouse.owned_by != user.id:
#         raise HTTPException(
#             status_code=403,
#             detail="You are not allowed to view this warehouse rents"
#         )
    
#     query = select(Rental).filter(Rental.warehouse_id == warehouse_id)
#     result = await db.execute(query)
#     rentals = result.scalars().all()
    
#     return rentals