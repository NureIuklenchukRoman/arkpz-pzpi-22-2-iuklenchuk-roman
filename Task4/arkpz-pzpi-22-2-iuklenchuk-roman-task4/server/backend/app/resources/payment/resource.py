from sqlalchemy import select
from fastapi import APIRouter, Depends

from app.database import get_db
from app.utils.auth import Authorization
from app.database.models import Rental, Payment

from .schema import PaymentResponseSchema


payment_router = APIRouter(prefix="/payments", tags=["payments"])


@payment_router.get("/", response_model=list[PaymentResponseSchema])
async def get_payments(db=Depends(get_db), user=Depends(Authorization())):
    user_rentals = select(Rental).filter(Rental.user_id == user.id)
    result = await db.execute(user_rentals)
    rentals = result.scalars().all()
    payments = []
    for rental in rentals:
        payment_query = select(Payment).filter(Payment.rental_id == rental.id)
        payment_result = await db.execute(payment_query)
        payment = payment_result.scalars().first()
        payments.append(payment)

    return payments


