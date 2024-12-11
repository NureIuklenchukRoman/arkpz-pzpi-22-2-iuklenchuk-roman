from datetime import datetime as duration
from datetime import timedelta
from sqlalchemy import select, delete
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.utils.auth import Authorization
from app.database.models import Warehouse, Rental, RentalStatus, PremiumService

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
    db.commit()

    return {"message": "Warehouse reserved successfully"}
