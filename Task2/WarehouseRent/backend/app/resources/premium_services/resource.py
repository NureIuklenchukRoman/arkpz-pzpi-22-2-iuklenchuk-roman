from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from .schema import (
    ServiceCreateSchema,
    ServiceDeleteSchema,
    ServiceResponseSchema,
    ServiceSchema,
    ServiceUpdateSchema
)

from app.database import get_db
from app.utils.auth import get_current_user, Authorization
from app.database.models import PremiumService, UserRole
from app.resources._shared.query import apply_filters_to_query, update_model


services_router = APIRouter(prefix="/services", tags=["services"])


@services_router.post("/create", response_model=ServiceResponseSchema)
async def create_service(service: ServiceCreateSchema,
                           user=Depends(Authorization(
                               allowed_roles=[UserRole.CUSTOMER])),
                           db=Depends(get_db)):
    new_service = PremiumService(
        warehouse_id=service.warehouse_id,
        name=service.name,
        description=service.description,
        price=service.price
    )
    db.add(new_service)
    await db.commit()
    return new_service



