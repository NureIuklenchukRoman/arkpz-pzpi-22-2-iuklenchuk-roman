import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Message, Lock, Payment, PremiumService, Rental, User, Warehouse, PaymentStatus, RentalStatus, UserRole
from app.database.base_model import Base
from app.database.conn import url

# Replace the following URL with your database URL
DATABASE_URL = url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data():
    session = SessionLocal()

    # Create some users
    users = [
        User(username="user1", last_name="Doe", first_name="John", email="john.doe@example.com", phone="1234567890", password="password1", role=UserRole.CUSTOMER),
        User(username="user2", last_name="Smith", first_name="Jane", email="jane.smith@example.com", phone="0987654321", password="password2", role=UserRole.ADMIN),
    ]

    session.add_all(users)
    session.commit()
    session.refresh(users)
    # Create some warehouses
    warehouses = [
        Warehouse(name="Warehouse 1", location="Location 1", size_sqm=100.0, price_per_day=10.0, owned_by=users[0].id),
        Warehouse(name="Warehouse 2", location="Location 2", size_sqm=200.0, price_per_day=20.0, owned_by=users[1].id),
    ]

    session.add_all(warehouses)
    session.commit()
    session.refresh(warehouses)

    # Create some locks
    locks = [
        Lock(ip="192.168.1.1", warehouse_id=warehouses[0].id, access_key="key1"),
        Lock(ip="192.168.1.2", warehouse_id=warehouses[1].id, access_key="key2"),
    ]

    session.add_all(locks)
    session.commit()
    session.refresh(locks)

    # Create some premium services
    premium_services = [
        PremiumService(warehouse_id=warehouses[0].id, name="Premium Service 1", description="Description 1", price=50.0),
        PremiumService(warehouse_id=warehouses[1].id, name="Premium Service 2", description="Description 2", price=100.0),
    ]

    session.add_all(premium_services)
    session.commit()
    session.refresh(premium_services)

    # Create some rentals
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=7)
    rentals = [
        Rental(user_id=users[0].id, warehouse_id=warehouses[0].id, start_date=start_date, end_date=end_date, total_price=70.0, status=RentalStatus.RESERVED),
        Rental(user_id=users[1].id, warehouse_id=warehouses[1].id, start_date=start_date, end_date=end_date, total_price=140.0, status=RentalStatus.COMPLETED),
    ]

    session.add_all(rentals)
    session.commit()
    session.refresh(rentals)

    # Create some payments
    payments = [
        Payment(rental_id=rentals[0].id, status=PaymentStatus.PENDING),
        Payment(rental_id=rentals[1].id, status=PaymentStatus.COMPLETED),
    ]

    session.add_all(payments)
    session.commit()
    session.refresh(payments)

    # Create some messages
    messages = [
        Message(user_id=users[0].id, text="Message 1", created_at=datetime.utcnow()),
        Message(user_id=users[1].id, text="Message 2", created_at=datetime.utcnow()),
    ]

    session.add_all(messages)
    session.commit()
    session.refresh(messages)

    session.close()

