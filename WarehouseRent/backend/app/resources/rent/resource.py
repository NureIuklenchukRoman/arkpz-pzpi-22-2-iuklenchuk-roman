from datetime import datetime as duration
from datetime import timedelta
from sqlalchemy import select, delete
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.utils.auth import Authorization
from app.database.models import Warehouse, Rental, RentalStatus

from .schemas import RentWarehouseSchema, WarehouseDetails


rent_router = APIRouter(prefix="/rent", tags=["rent"])


def calculate_price(start_date, end_date, price):
    days = (start_date - end_date).days
    price = days * price
    return price


@rent_router.get("/details/{warehouse_id}", response_model=WarehouseDetails)
async def get_rent_details(warehouse_id: int, db=Depends(get_db)):

    warehouse_query = select(Warehouse).filter(Warehouse.id == warehouse_id)
    warehouse_result = await db.execute(warehouse_query)
    warehouse = warehouse_result.scalar_one_or_none()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    query = select(Rental).filter(Rental.warehouse_id == warehouse_id)
    result = await db.execute(query)
    rentals = result.scalars().all()

    busy_dates = []
    for rental in rentals:
        dates = []
        cur_date = rental.start_date

        while cur_date <= rental.end_date:
            dates.append(cur_date)
            cur_date += timedelta(days=1)

        busy_dates.extend(dates)

    response = dict(
        id=warehouse.id,
        name=warehouse.name,
        location=warehouse.location,
        price_per_day=warehouse.price_per_day,
        busy_dates=busy_dates
    )

    return response


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
        total_price=calculate_price(
            warehouse_data.start_date, warehouse_data.end_date, warehouse.price_per_day),
        status=RentalStatus.RESERVED
    )
    db.add(rental)
    db.commit()

    return {"message": "Warehouse reserved successfully"}
