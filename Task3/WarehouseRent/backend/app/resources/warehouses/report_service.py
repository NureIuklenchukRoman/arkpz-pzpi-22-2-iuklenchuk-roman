from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import pandas as pd
from app.database.models import Warehouse, Rental


# async def get_rental_data(db: AsyncSession):
#     result = await db.execute(select(Rental))
#     rentals = result.scalars().all()

#     data = [
#         {
#             "user_id": rental.user_id,
#             "warehouse_id": rental.warehouse_id,
#             "start_date": rental.start_date,
#             "end_date": rental.end_date,
#             "total_price": rental.total_price
#         }
#         for rental in rentals
#     ]

#     df = pd.DataFrame(data)

#     df['start_date'] = pd.to_datetime(df['start_date'])
#     df['end_date'] = pd.to_datetime(df['end_date'])

#     return df


# async def calculate_occupancy_rate(db: AsyncSession):
#     data = await get_rental_data(db)
#     if data.empty:
#         return 0.0
#     total_days = (data['end_date'] - data['start_date']).dt.days.sum()
#     total_warehouses = await db.scalar(select(func.count(Warehouse.id)))
#     occupancy_rate = total_days / (total_warehouses * 365)
#     return occupancy_rate


# async def total_revenue(db: AsyncSession):
#     data = await get_rental_data(db)
#     if data.empty:
#         return 0.0
#     return data['total_price'].sum()


# async def average_rental_duration(db: AsyncSession):
#     data = await get_rental_data(db)
#     if data.empty:
#         return 0.0
#     return (data['end_date'] - data['start_date']).dt.days.mean()


# async def generate_report(db: AsyncSession):
#     report = {
#         "total_revenue": await total_revenue(db),
#         "occupancy_rate": await calculate_occupancy_rate(db),
#         "average_rental_duration": await average_rental_duration(db),
#     }
#     return report

async def get_rental_data(db: AsyncSession):
    result = await db.execute(select(Rental))
    rentals = result.scalars().all()
    
    data = [
        {
            "user_id": rental.user_id,
            "warehouse_id": rental.warehouse_id,
            "start_date": rental.start_date,
            "end_date": rental.end_date,
            "total_price": rental.total_price
        }
        for rental in rentals
    ]
    
    df = pd.DataFrame(data)
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    
    return df

async def calculate_occupancy_rate(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return 0.0
    total_days = (data['end_date'] - data['start_date']).dt.days.sum()
    total_warehouses = await db.scalar(select(func.count(Warehouse.id)))
    occupancy_rate = total_days / (total_warehouses * 365)
    return occupancy_rate

async def calculate_occupancy_rate_by_period(db: AsyncSession, period: str):
    data = await get_rental_data(db)
    if data.empty:
        return {}

    if period == 'month':
        data['period'] = data['start_date'].dt.to_period('M')
    elif period == 'year':
        data['period'] = data['start_date'].dt.to_period('Y')
    
    total_warehouses = await db.scalar(select(func.count(Warehouse.id)))
    occupancy_rate = data.groupby('period').apply(
        lambda x: (x['end_date'] - x['start_date']).dt.days.sum() / (total_warehouses * x['period'].dt.days_in_month.sum())
    )
    
    occupancy_rate.index = occupancy_rate.index.astype(str)  # Convert PeriodIndex to string
    return occupancy_rate.to_dict()

async def total_revenue(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return 0.0
    return data['total_price'].sum()

async def revenue_growth_rate(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return 0.0
    
    data['year'] = data['start_date'].dt.year
    yearly_revenue = data.groupby('year')['total_price'].sum()
    growth_rate = yearly_revenue.pct_change().fillna(0) * 100
    
    return growth_rate.to_dict()

async def average_rental_duration(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return 0.0
    return (data['end_date'] - data['start_date']).dt.days.mean() / 7  # in weeks

async def utilization_rate(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return 0.0
    
    total_days = (data['end_date'] - data['start_date']).dt.days.sum()
    total_warehouses = await db.scalar(select(func.count(Warehouse.id)))
    total_possible_days = total_warehouses * 365
    
    utilization_rate = total_days / total_possible_days
    return utilization_rate

async def revenue_per_warehouse(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return 0.0
    
    revenue_per_warehouse = data.groupby('warehouse_id')['total_price'].sum().mean()
    return revenue_per_warehouse

async def top_performing_warehouses(db: AsyncSession):
    data = await get_rental_data(db)
    if data.empty:
        return []
    
    top_warehouses = data.groupby('warehouse_id')['total_price'].sum().nlargest(5)
    return top_warehouses.index.tolist()

async def generate_report(db: AsyncSession):
    report = {
        "total_revenue": await total_revenue(db),
        "occupancy_rate": await calculate_occupancy_rate(db),
        "average_rental_duration": await average_rental_duration(db),
        "utilization_rate": await utilization_rate(db),
        "revenue_per_warehouse": await revenue_per_warehouse(db),
        "revenue_growth_rate": await revenue_growth_rate(db),
        "top_performing_warehouses": await top_performing_warehouses(db),
        "monthly_occupancy_rate": await calculate_occupancy_rate_by_period(db, 'month'),
        "yearly_occupancy_rate": await calculate_occupancy_rate_by_period(db, 'year'),
    }
    return report