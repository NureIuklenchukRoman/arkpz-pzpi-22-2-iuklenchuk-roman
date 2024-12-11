from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.database import get_db
from app.database.models import Warehouse, Rental, User, Lock
from app.utils.auth import Authorization
from app.resources._shared.query import update_model

from .schemas import LockResponseSchema, LockCreateSchema


locks_router = APIRouter(prefix="/locks", tags=["locks"])


@locks_router.get("/", response_model=list[LockResponseSchema])
async def get_locks(user=Depends(Authorization()), db=Depends(get_db)):
    warehouses_query = select(Warehouse).filter(Warehouse.owned_by == user.id)
    warehouses_result = await db.execute(warehouses_query)
    warehouses = warehouses_result.scalars().all()
    
    results = []
    for warehouse in warehouses:
        query = select(Lock).filter(Lock.warehouse_id == warehouse.id)
        result = await db.execute(query)
        locks = result.scalars().all()
        
        for lock in locks:
            results.append(
                dict(
                    id=lock.id,
                    warehouse_id=lock.warehouse_id,
                    access_key=lock.access_key,
                )
            )
            
    return results


@locks_router.post("/", response_model=LockResponseSchema)
async def create_lock(lock: LockCreateSchema, user=Depends(Authorization()), db=Depends(get_db)):
    new_lock = Lock(
        warehouse_id=lock.warehouse_id,
    )
    db.add(new_lock)
    await db.commit()
    return new_lock


@locks_router.delete("/{lock_id}", response_model=LockResponseSchema)
async def delete_lock(lock_id: int, user=Depends(Authorization()), db=Depends(get_db)):
    query = select(Lock).filter(Lock.id == lock_id)
    result = await db.execute(query)
    lock = result.scalars().first()
    
    if lock is None:
        raise HTTPException(status_code=404, detail="Lock not found")
    
    await db.delete(lock)
    await db.commit()
    return lock