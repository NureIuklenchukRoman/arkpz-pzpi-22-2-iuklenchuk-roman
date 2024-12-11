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
    WarehouseResponseSchema
)

from app.database import get_db
from app.utils.auth import get_current_user, Authorization
from app.database.models import Warehouse, UserRole
from app.resources._shared.query import apply_filters_to_query, update_model


warehouse_router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@warehouse_router.get("/", response_model=list[WarehouseResponseSchema])
async def get_all_warehouses(db=Depends(get_db),
                             query_params: WarehouseQuerySchema = Depends()):
    query = select(Warehouse)
    query = apply_filters_to_query(query, Warehouse, query_params)

    result = await db.execute(query)
    warehouses = result.scalars().all()
    return warehouses


@warehouse_router.post("/create", response_model=WarehouseResponseSchema)
async def create_warehouse(warehouse: WarehouseCreateSchema,
                           user=Depends(Authorization(
                               allowed_roles=[UserRole.CUSTOMER])),
                           db=Depends(get_db)):
    new_warehouse = Warehouse(
        name=warehouse.name,
        location=warehouse.location,
        size_sqm=warehouse.size_sqm,
        is_available=warehouse.is_available,
        price_per_day=warehouse.price_per_day,
        available_premium_services=warehouse.available_premium_services,
        owned_by=user.id
    )
    db.add(new_warehouse)
    await db.commit()
    return new_warehouse


@warehouse_router.put("/update", response_model=WarehouseResponseSchema)
async def update_warehouse(warehouse_data: WarehouseUpdateSchema,
                           user=Depends(Authorization(
                               allowed_roles=[UserRole.CUSTOMER])),
                           db=Depends(get_db)):

    query = select(Warehouse).filter(Warehouse.id == warehouse_data.id)
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

    update_model(warehouse, warehouse_data)

    await db.commit()
    return warehouse
