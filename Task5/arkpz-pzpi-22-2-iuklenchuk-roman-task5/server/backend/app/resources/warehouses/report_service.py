import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Warehouse, Rental


async def check_warehouse_owner(db, user, id):
    query = select(Warehouse).filter(Warehouse.id == id)
    result = await db.execute(query)
    warehouse = result.scalars().first()
    if warehouse.owned_by != user.id:
        return False
    return True


async def get_rental_data(db: AsyncSession, user):
    result = await db.execute(select(Rental))
    rentals = result.scalars().all()

    data = []
    for rental in rentals:
        if await check_warehouse_owner(db, user, rental.warehouse_id):
            data.append({
                "user_id": rental.user_id,
                "warehouse_id": rental.warehouse_id,
                "start_date": rental.start_date,
                "end_date": rental.end_date,
                "total_price": rental.total_price
            })

    df = pd.DataFrame(data)

    if df.empty:
        return df

    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])

    return df


async def total_revenue(db: AsyncSession, user):
    data = await get_rental_data(db, user)
    if data.empty:
        return 0.0
    return data['total_price'].sum()


async def revenue_growth_rate(db: AsyncSession, user):
    data = await get_rental_data(db, user)
    if data.empty:
        return 0.0

    data['year'] = data['start_date'].dt.year
    yearly_revenue = data.groupby('year')['total_price'].sum()
    growth_rate = yearly_revenue.pct_change().fillna(0) * 100

    return growth_rate.to_dict()


async def average_rental_duration(db: AsyncSession, user):
    data = await get_rental_data(db, user)
    if data.empty:
        return 0.0
    return (data['end_date'] - data['start_date']).dt.days.mean()


async def revenue_per_warehouse(db: AsyncSession, user):
    data = await get_rental_data(db, user)
    if data.empty:
        return 0.0

    revenue_per_warehouse = data.groupby(
        'warehouse_id')['total_price'].sum().mean()
    return revenue_per_warehouse


async def top_performing_warehouses(db: AsyncSession, user):
    data = await get_rental_data(db, user)
    if data.empty:
        return []

    top_warehouses = data.groupby('warehouse_id')[
        'total_price'].sum().nlargest(5)
    return top_warehouses.index.tolist()


async def generate_report(db: AsyncSession, user):
    report = {
        "total_revenue": await total_revenue(db, user),
        "average_rental_duration": await average_rental_duration(db, user),
        "revenue_per_warehouse": await revenue_per_warehouse(db, user),
        "revenue_growth_rate": await revenue_growth_rate(db, user),
        "top_performing_warehouses": await top_performing_warehouses(db, user),
    }
    return report
