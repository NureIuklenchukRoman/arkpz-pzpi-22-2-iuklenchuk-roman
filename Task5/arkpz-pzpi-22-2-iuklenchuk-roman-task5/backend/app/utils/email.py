import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.celery import celery_app
from app.celery.tasks import DatabaseTask
from app.database.models import User, Message


smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_username = os.getenv('SMTP_USERNAME', 'test.senderem@gmail.com')
smtp_password = os.getenv('SMTP_PASSWORD', 'santskoggbtuuefz')


@celery_app.task(base=DatabaseTask, bind=True, name="send_email", queue='cpu')
def send_email(self, user_id, text, subject):
    db = self.session
    user = db.query(User).get(user_id)
    user_email = user.email
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(text, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print(f'Email sent to {user_email}')
        m = Message(user_id=1, text=f"Email sent to {user_email}")
        db.add(m)
        db.commit()
    except Exception as e:
        print(f'Failed to send email to {user_email}. Error: {e}')
        m = Message(
            user_id=1, text=f"Failed to send email to {user_email}. Error: {e}")
        db.add(m)
        db.commit()