from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import get_db
from app.database.models import Warehouse, Rental, User
from app.utils.auth import Authorization
from app.resources._shared.query import update_model

from .schemas import RentalResponseSchema, UserResponseSchema, UserUpdateSchema


user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/my_rents", response_model=list[RentalResponseSchema])
async def get_my_rent(user=Depends(Authorization()), db=Depends(get_db)):
    query = select(Rental).filter(Rental.user_id == user.id)
    rental_result = await db.execute(query)
    rentals = rental_result.scalars().all()

    results = []
    for rental in rentals:
        warehouse_query = select(Warehouse).filter(
            Warehouse.id == rental.warehouse_id)
        warehouse_result = await db.execute(warehouse_query)
        warehouse = warehouse_result.scalar_one_or_none()

        results.append(
            dict(
                id=rental.id,
                warehouse_name=warehouse.name,
                warehouse_location=warehouse.location,
                start_date=rental.start_date,
                end_date=rental.end_date,
                status=rental.status,
                total_price=rental.total_price
            )
        )

    return results


@user_router.get("/my_rents/{rent_id}", response_model=RentalResponseSchema)
async def get_my_rent(rent_id: int, user=Depends(Authorization()), db=Depends(get_db)):
    query = select(Rental).filter(Rental.id == rent_id)
    rental_result = await db.execute(query)
    rental = rental_result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=404,
            detail="Rental not found"
        )

    warehouse_query = select(Warehouse).filter(
        Warehouse.id == rental.warehouse_id)
    warehouse_result = await db.execute(warehouse_query)
    warehouse = warehouse_result.scalar_one_or_none()

    return dict(
        id=rental.id,
        warehouse_name=warehouse.name,
        warehouse_location=warehouse.location,
        start_date=rental.start_date,
        end_date=rental.end_date,
        status=rental.status,
        total_price=rental.total_price
    )


@user_router.put("/me", response_model=UserResponseSchema)
async def update_user_info(user_data: UserUpdateSchema, user=Depends(Authorization()), db=Depends(get_db)):
    update_model(user, user_data.dict(exclude_unset=True))
    await db.commit()
    return user


@user_router.get("/me", response_model=UserResponseSchema)
async def get_user_info(user=Depends(Authorization()), db=Depends(get_db)):
    return user
