import random
from datetime import timedelta
from datetime import datetime as dt

from app.celery import celery_app
from app.database.models import Rental, RentalStatus, User, Message, Lock
from app.celery.tasks import DatabaseTask

@celery_app.task(base=DatabaseTask, bind=True, name="check_expiring_rentals", queue='cpu')
def check_expiring_rentals(self):
    from app.utils.email import send_email

    rentals = self.session.query(Rental).filter(
        Rental.end_date <= (dt.utcnow()+timedelta(days=1))).all()

    # for rental in rentals:
    #     send_email.delay(rental.user_id,
    #                "Your rental is expiring tomorrow", "Rent expiration")

    today_rentals = self.session.query(Rental).filter(
        Rental.end_date == dt.utcnow().date()).all()
    for today_rental in today_rentals:
        today_rental.status = RentalStatus.COMPLETED
        # send_email.delay(today_rental.user_id,
        #            "Your rental has been completed", "Rent completion")
        
    today_rents_to_start = self.session.query(Rental).filter(
        Rental.start_date == dt.utcnow().date(), Rental.status == RentalStatus.RESERVED).all()
    for today_rent_to_start in today_rents_to_start:
        lock = self.session.query(Lock).filter(Lock.warehouse_id == today_rent_to_start.warehouse_id).first()
        lock.access_key = str(random.randint(10**9, 10**10 - 1))
        today_rent_to_start.status = RentalStatus.ONGOING
    self.session.commit()
    
