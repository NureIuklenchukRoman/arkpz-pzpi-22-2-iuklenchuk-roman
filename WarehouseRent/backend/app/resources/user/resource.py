from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.database import get_db
from app.database.models import Warehouse, Rental
from app.utils.auth import Authorization

from .schemas import RentalResponseSchema


user_router = APIRouter(prefix="/user", tags=["user"])
#comment

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
