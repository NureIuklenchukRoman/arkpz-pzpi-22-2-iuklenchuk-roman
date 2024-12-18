from sqlalchemy import select, delete
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.utils.auth import Authorization, check_if_user_blocked
from app.database.models import PremiumService, UserRole, Warehouse
from app.resources._shared.query import apply_filters_to_query, update_model

from .schema import (
    ServiceCreateSchema,
    ServiceResponseSchema,
    ServiceUpdateSchema
)


services_router = APIRouter(prefix="/services", tags=["services"])


@services_router.post("/", response_model=ServiceResponseSchema)
async def create_service(service: ServiceCreateSchema,
                           user=Depends(Authorization(
                               allowed_roles=[UserRole.SELLER])),
                           db=Depends(get_db)):
    check_if_user_blocked(user)
    new_service = PremiumService(
        warehouse_id=service.warehouse_id,
        name=service.name,
        description=service.description,
        price=service.price
    )
    db.add(new_service)
    await db.commit()
    return new_service


@services_router.get("/warehouse-services/{warehouse_id}", response_model=list[ServiceResponseSchema])
async def get_warehouse_services(warehouse_id: int, db=Depends(get_db)):
    query = select(PremiumService).filter(PremiumService.warehouse_id == warehouse_id)
    result = await db.execute(query)
    services = result.scalars().all()
    return services

@services_router.get("/", response_model=list[ServiceResponseSchema])
async def get_all_services(db=Depends(get_db), user=Depends(Authorization(allowed_roles=[UserRole.ADMIN]))):
    query = select(PremiumService)
    result = await db.execute(query)
    services = result.scalars().all()
    return services


@services_router.get("/my-services", response_model=list[ServiceResponseSchema])
async def get_my_services(db=Depends(get_db), user=Depends(Authorization(allowed_roles=[UserRole.SELLER]))):
    warehouses_query = select(Warehouse).filter(Warehouse.owned_by == user.id)
    warehouses_result = await db.execute(warehouses_query)
    warehouses = warehouses_result.scalars().all()
    
    res = []
    for warehouse in warehouses:
        query = select(PremiumService).filter(PremiumService.warehouse_id == warehouse.id)
        result = await db.execute(query)
        services = result.scalars().all()
        res.extend(services)
    
    return res


@services_router.put("/{service_id}", response_model=ServiceResponseSchema)
async def update_service(service_id: int, service_updated: ServiceUpdateSchema,
                         user=Depends(Authorization(
                             allowed_roles=[UserRole.SELLER])),
                         db=Depends(get_db)):
    check_if_user_blocked(user)
    query = select(PremiumService).filter(PremiumService.id == service_id)
    result = await db.execute(query)
    service = result.scalars().first()

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    update_model(service, service_updated.dict(exclude_unset=True))
    await db.commit()
    return service


@services_router.delete("/{service_id}", response_model=ServiceResponseSchema)
async def delete_service(service_id: int, user=Depends(Authorization(
    allowed_roles=[UserRole.SELLER])),
                         db=Depends(get_db)):
    check_if_user_blocked(user)
    query = select(PremiumService).filter(PremiumService.id == service_id)
    result = await db.execute(query)
    service = result.scalars().first()

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    await db.delete(service)
    await db.commit()
    return service

