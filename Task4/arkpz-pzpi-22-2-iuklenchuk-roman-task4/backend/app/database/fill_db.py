import os
import random
import asyncio
from faker import Faker
from datetime import timedelta
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from ..database.models import User, Warehouse, Lock, Message, Payment, PremiumService, Rental, PaymentStatus, RentalStatus, UserRole

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:" \
    f"{os.getenv('POSTGRES_PASSWORD')}@" \
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', '5432')}/" \
    f"{os.getenv('POSTGRES_DB')}"


engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


fake = Faker()


async def create_users(session, num_users=20):
    users = []
    for _ in range(num_users):
        user = User(
            username=fake.user_name(),
            last_name=fake.last_name(),
            first_name=fake.first_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            password=fake.password(),
            role=random.choice(list(UserRole)),
            is_blocked=random.choice([True, False])
        )
        users.append(user)
    session.add_all(users)
    await session.commit()


async def create_warehouses(session, num_warehouses=100):
    users = await session.execute(select(User))
    user_list = users.scalars().all()
    warehouses = []
    for _ in range(num_warehouses):
        warehouse = Warehouse(
            name=fake.company(),
            location=fake.address(),
            size_sqm=random.uniform(50, 500),
            price_per_day=random.uniform(10, 100),
            owned_by=random.choice(user_list).id
        )
        warehouses.append(warehouse)
    session.add_all(warehouses)
    await session.commit()


async def create_locks(session, num_locks=100):
    warehouses = await session.execute(select(Warehouse))
    warehouse_list = warehouses.scalars().all()
    locks = []
    for _ in range(num_locks):
        lock = Lock(
            ip=fake.ipv4(),
            warehouse_id=random.choice(warehouse_list).id,
            access_key=str(random.randint(10**9, 10**10 - 1))
        )
        locks.append(lock)
    session.add_all(locks)
    await session.commit()


async def create_messages(session, num_messages=100):
    users = await session.execute(select(User))
    user_list = users.scalars().all()
    messages = []
    for _ in range(num_messages):
        message = Message(
            user_id=random.choice(user_list).id,
            text=fake.text(),
            created_at=fake.date_time_this_year()
        )
        messages.append(message)
    session.add_all(messages)
    await session.commit()


async def create_rentals(session, num_rentals=100):
    users = await session.execute(select(User))
    user_list = users.scalars().all()
    warehouses = await session.execute(select(Warehouse))
    warehouse_list = warehouses.scalars().all()
    rentals = []
    for _ in range(num_rentals):
        start_date = fake.date_between(start_date='-2y', end_date='today')
        end_date = start_date + timedelta(days=random.randint(1, 30))
        rental = Rental(
            user_id=random.choice(user_list).id,
            warehouse_id=random.choice(warehouse_list).id,
            start_date=start_date,
            end_date=end_date,
            total_price=random.uniform(100, 1000),
            status=random.choice(list(RentalStatus))
        )
        rentals.append(rental)
    session.add_all(rentals)
    await session.commit()


async def create_payments(session, num_payments=100):
    rentals = await session.execute(select(Rental))
    rental_list = rentals.scalars().all()
    payments = []
    for _ in range(num_payments):
        payment = Payment(
            rental_id=random.choice(rental_list).id,
            status=random.choice(list(PaymentStatus)),
            created_at=fake.date_time_this_year()
        )
        payments.append(payment)
    session.add_all(payments)
    await session.commit()


async def create_premium_services(session, num_services=100):
    warehouses = await session.execute(select(Warehouse))
    warehouse_list = warehouses.scalars().all()
    services = []
    for _ in range(num_services):
        service = PremiumService(
            warehouse_id=random.choice(warehouse_list).id,
            name=fake.word(),
            description=fake.text(),
            price=random.uniform(10, 100)
        )
        services.append(service)
    session.add_all(services)
    await session.commit()


async def main():
    async with SessionLocal() as session:
        await create_users(session)
        await create_warehouses(session)
        await create_locks(session)
        await create_messages(session)
        await create_rentals(session)
        await create_payments(session)
        await create_premium_services(session)

if __name__ == "__main__":
    asyncio.run(main())
