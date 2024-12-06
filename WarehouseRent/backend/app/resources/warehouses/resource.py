from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from .schema import (
    WarehouseCreateSchema,
    WarehouseUpdateSchema,
    WarehouseDeleteSchema,
    WarehouseSchema,
    WarehouseQuerySchema
)

from app.database import get_db
from app.utils.auth import get_current_user
from app.database.models import Warehouse, UserRole
from app.resources._shared.query import apply_filters_to_query


warehouse_router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@warehouse_router.get("/", response_model=list[WarehouseSchema])
async def get_all_warehouses(
    db=Depends(get_db),
    query_params: WarehouseQuerySchema = Depends()
):
    query = select(Warehouse)

    query = apply_filters_to_query(query, Warehouse, query_params)

    result = await db.execute(query)
    warehouses = result.scalars().all()
    return warehouses


@warehouse_router.post("/create", response_model=WarehouseCreateSchema)
async def create_warehouse(warehouse: WarehouseCreateSchema, user=Depends(get_current_user), db=Depends(get_db)):
    # if user.role != UserRole.ADMIN:
    #     raise HTTPException(
    #         status_code=403, detail="You are not authorized to create a warehouse")
    new_warehouse = Warehouse(
        name=warehouse.name,
        location=warehouse.location,
        size_sqm=warehouse.size_sqm,
        is_available=warehouse.is_available,
        price_per_day=warehouse.price_per_day,
        premium_services=warehouse.premium_services
    )
    db.add(new_warehouse)
    await db.commit()
    return new_warehouse
