from datetime import timedelta
from datetime import datetime as dt

from app.celery import celery_app
from app.database.models import Rental, RentalStatus, User, Message
from app.celery.tasks import DatabaseTask
from app.utils.email import send_email


@celery_app.task(base=DatabaseTask, bind=True, name="check_expiring_rentals", queue='cpu')
def check_expiring_rentals(self):
    rentals = self.session.query(Rental).filter(
        Rental.end_date <= (dt.utcnow()+timedelta(days=1))).all()

    for rental in rentals:
        send_email.delay(rental.user_id,
                   "Your rental is expiring tomorrow", "Rent expiration")

    today_rentals = self.session.query(Rental).filter(
        Rental.end_date == dt.utcnow()).all()
    for today_rental in today_rentals:
        today_rental.status = RentalStatus.COMPLETED
        send_email.delay(today_rental.user_id,
                   "Your rental has been completed", "Rent completion")
