from sqlalchemy import select
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.database.models import Warehouse, Lock, UserRole
from app.utils.auth import Authorization, check_if_user_blocked

from .schemas import LockResponseSchema, LockCreateSchema, LockUnlockSchema


async def check_lock_owner(db, lock, user):
    warehouse_query = select(Warehouse).filter(Warehouse.id == lock.warehouse_id)
    result = await db.execute(warehouse_query)
    warehouse = result.scalars().first()
    
    if warehouse.owned_by != user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this lock")
    

locks_router = APIRouter(prefix="/locks", tags=["locks"])


@locks_router.get("/{lock_id}/{lock_ip}", response_model=LockResponseSchema)
async def get_lock(lock_id: int, lock_ip: str, db=Depends(get_db)):
    query = select(Lock).filter(Lock.id == lock_id, Lock.ip == lock_ip)
    result = await db.execute(query)
    lock = result.scalars().first()
    
    if lock is None:
        raise HTTPException(status_code=404, detail="Lock not found")
    
    return lock


@locks_router.post("/unlock/{lock_id}/{lock_ip}")
async def get_unlock_lock(lock_id: int, lock_ip: str, key: LockUnlockSchema,db=Depends(get_db)):
    query = select(Lock).filter(Lock.id == lock_id, Lock.ip == lock_ip)
    result = await db.execute(query)
    lock = result.scalars().first()
    
    if lock is None:
        raise HTTPException(status_code=404, detail="Lock not found")
    
    if lock.access_key == key.access_key:
        return JSONResponse(content={"status": 1, "message": "Lock opened successfully"})
    else:
        return JSONResponse(content={"status": 0, "message": "Incorrect key"})


@locks_router.get("/", response_model=list[LockResponseSchema])
async def get_locks(user=Depends(Authorization(allowed_roles=[UserRole.SELLER])), db=Depends(get_db)):
    check_if_user_blocked(user)
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
                    ip=lock.ip
                )
            )
            
    return results


@locks_router.post("/", response_model=LockResponseSchema)
async def create_lock(lock: LockCreateSchema, user=Depends(Authorization(allowed_roles=[UserRole.SELLER])), db=Depends(get_db)):
    check_if_user_blocked(user)
    new_lock = Lock(
        warehouse_id=lock.warehouse_id,
        ip=lock.ip,
    )
    await check_lock_owner(db, lock, user)

    db.add(new_lock)
    await db.commit()
    return new_lock


@locks_router.delete("/{lock_id}", response_model=LockResponseSchema)
async def delete_lock(lock_id: int, user=Depends(Authorization(allowed_roles=[UserRole.SELLER])), db=Depends(get_db)):
    check_if_user_blocked(user)
    query = select(Lock).filter(Lock.id == lock_id)
    result = await db.execute(query)
    lock = result.scalars().first()
    
    await check_lock_owner(db, lock, user)

    if lock is None:
        raise HTTPException(status_code=404, detail="Lock not found")
    
    await db.delete(lock)
    await db.commit()
    return lock