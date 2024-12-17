from .calery_app import celery_app

from celery.schedules import crontab
# from app.resources.rent.tasks import check_expiring_rentals

# @celery_app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # sender.add_periodic_task(crontab(hour=23, minute=0), check_expiring_rentals.s(), name="check_expiring_rentals")
#     # sender.add_periodic_task(60.0, check_expiring_rentals.s(), name="check_expiring_rentals")
#     pass