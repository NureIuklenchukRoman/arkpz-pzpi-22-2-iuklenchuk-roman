from datetime import timedelta
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from .schema import (
    WarehouseCreateSchema,
    WarehouseUpdateSchema,
    WarehouseDeleteSchema,
    WarehouseSchema,
    WarehouseQuerySchema,
    WarehouseResponseSchema,
    WarehouseDetails
)

from app.database import get_db
from app.utils.auth import get_current_user, Authorization
from app.database.models import Warehouse, UserRole, Rental
from app.resources._shared.query import apply_filters_to_query, update_model


warehouse_router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@warehouse_router.get("/", response_model=list[WarehouseResponseSchema])
async def get_all_warehouses(db=Depends(get_db),
                             user=Depends(Authorization(
                                allowed_roles=[])),
                             query_params: WarehouseQuerySchema = Depends()):
    query = select(Warehouse)
    query = apply_filters_to_query(query, Warehouse, query_params)

    result = await db.execute(query)
    warehouses = result.scalars().all()
    return warehouses


@warehouse_router.get("/{warehouse_id}", response_model=WarehouseDetails)
async def get_warehouse_details(warehouse_id: int, 
                            user=Depends(Authorization(
                                allowed_roles=[])),
                            db=Depends(get_db)):

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


@warehouse_router.post("/", response_model=WarehouseResponseSchema)
async def create_warehouse(warehouse: WarehouseCreateSchema,
                           user=Depends(Authorization(
                               allowed_roles=[UserRole.ADMIN])),
                           db=Depends(get_db)):
    new_warehouse = Warehouse(
        name=warehouse.name,
        location=warehouse.location,
        size_sqm=warehouse.size_sqm,
        price_per_day=warehouse.price_per_day,
        owned_by=user.id
    )
    db.add(new_warehouse)
    await db.commit()
    return new_warehouse


@warehouse_router.put("/{warehouse_id}", response_model=WarehouseResponseSchema)
async def update_warehouse(warehouse_id: int, warehouse_data: WarehouseUpdateSchema,
                           user=Depends(Authorization(
                               allowed_roles=[UserRole.ADMIN])),
                           db=Depends(get_db)):

    query = select(Warehouse).filter(Warehouse.id == warehouse_id)
    result = await db.execute(query)
    warehouse = result.scalar_one_or_none()

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    if warehouse.owned_by != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this warehouse because you not own it"
        )

    update_model(warehouse, warehouse_data.dict(exclude_unset=True))

    await db.commit()
    return warehouse
