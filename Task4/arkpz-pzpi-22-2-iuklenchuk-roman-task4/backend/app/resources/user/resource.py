from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.utils.auth import Authorization
from app.resources._shared.query import update_model
from app.database.models import Warehouse, Rental, User, UserRole, Lock, RentalStatus

from .schemas import RentalResponseSchema, UserResponseSchema, UserUpdateSchema, LockResponseSchema


user_router = APIRouter(prefix="/users", tags=["users"])


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


@user_router.get("/my_locks", response_model=list[LockResponseSchema])
async def get_my_locks(user=Depends(Authorization()), db=Depends(get_db)):
    query = select(Rental).filter(Rental.user_id == user.id, Rental.status == RentalStatus.RESERVED)
    rental_result = await db.execute(query)
    rental = rental_result.scalars().all()
    warehouse_ids = [rent.warehouse_id for rent in rental]
    if not rental:
        raise HTTPException(
            status_code=404,
            detail="Rental not found"
        )

    warehouse_query = select(Warehouse).filter(
        Warehouse.id.in_(warehouse_ids))
    warehouse_result = await db.execute(warehouse_query)
    warehouse = warehouse_result.scalars().all()
    warehouse_ids = [ware.id for ware in warehouse]
    
    lock_query = select(Lock).filter(Lock.warehouse_id.in_(warehouse_ids))
    lock_result = await db.execute(lock_query)
    locks = lock_result.scalars().all()

    return locks


@user_router.put("/me", response_model=UserResponseSchema)
async def update_user_info(user_data: UserUpdateSchema, user=Depends(Authorization()), db=Depends(get_db)):
    update_model(user, user_data.dict(exclude_unset=True))
    await db.commit()
    return user


@user_router.get("/me", response_model=UserResponseSchema)
async def get_user_info(user=Depends(Authorization()), db=Depends(get_db)):
    return user


@user_router.get("/", response_model=list[UserResponseSchema])
async def get_all_users(db=Depends(get_db), user=Depends(Authorization(allowed_roles=[UserRole.ADMIN]))):
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


async def get_user_warehouses(db, user):
    user_warehouses_query = select(Warehouse).filter(Warehouse.owned_by == user.id)
    user_warehouses_result = await db.execute(user_warehouses_query)
    user_warehouses = user_warehouses_result.scalars().all()
    return user_warehouses


@user_router.get("/block_user", response_model=UserResponseSchema)
async def block_user(user_id: int, db=Depends(get_db), user=Depends(Authorization(allowed_roles=[UserRole.ADMIN]))):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    user.is_blocked = True
    
    user_warehouses = await get_user_warehouses(db, user)
    for warehouse in user_warehouses:
        warehouse.is_blocked = True
    await db.commit()
    return user


@user_router.get("/unblock_user", response_model=UserResponseSchema)
async def unblock_user(user_id: int, db=Depends(get_db), user=Depends(Authorization(allowed_roles=[UserRole.ADMIN]))):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    user.is_blocked = False
    
    user_warehouses = await get_user_warehouses(db, user)
    for warehouse in user_warehouses:
        warehouse.is_blocked = False
    await db.commit()
    return user