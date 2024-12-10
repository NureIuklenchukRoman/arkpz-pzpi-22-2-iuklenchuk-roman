from datetime import datetime as dt
from datetime import timedelta

from app.celery import celery_app
from app.database.models import Rental, RentalStatus
from app.celery.tasks import DatabaseTask


def send_email(user_id, text):
    pass

@celery_app.task(base=DatabaseTask, bind=True, name="check_expiring_rentals", queue='cpu')
def check_expiring_rentals(self):
    rentals = self.session.query(Rental).filter(Rental.end_date == dt.utcnow() + timedelta(days=1)).all()
    for rental in rentals:
        send_email(rental.user_id, "Your rental is expiring tomorrow")

    today_rentals = rentals = self.session.query(Rental).filter(Rental.end_date == dt.utcnow()).all()
    for today_rental in today_rentals:
        today_rental.status = RentalStatus.COMPLETED
        send_email(today_rental.user_id, "Your rental has been completed")

