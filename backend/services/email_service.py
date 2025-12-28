import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from config import config
import threading

class EmailService:
    def __init__(self):
        self.server = config.SMTPSERVER
        self.port = config.SMTPPORT
        self.username = config.SMTPUSERNAME
        self.password = config.SMTPPASSWORD
        self.sender = config.SENDEREMAIL
        self.enabled = config.ENABLEEMAILNOTIFICATIONS

    def send_email_async(self, recipient_email: str, subject: str, body: str):
        """Send email asynchronously to avoid blocking the main thread"""
        if not self.enabled:
            return

        thread = threading.Thread(
            target=self._send_email_thread,
            args=(recipient_email, subject, body)
        )
        thread.start()

    def _send_email_thread(self, recipient_email: str, subject: str, body: str):
        """Internal method to execute SMTP sending"""
        try:
            msg = MIMEMultipart()
            # User friendliness: "MedPulse Official <email>"
            msg['From'] = f"MedPulse Official <{self.sender}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Check if using default credentials (placeholder)
            if "your-email" in self.username:
                logger.warning(f"Email skipped: Default SMTP credentials detected. Would have sent to {recipient_email}")
                return

            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.sender, recipient_email, text)
            server.quit()
            logger.info(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")

    def send_appointment_confirmation(self, recipient_email: str, user_name: str, date: str, time: str, doctor: str):
        subject = f"Appointment Confirmed - {config.CLINICNAME}"
        body = f"""Dear {user_name},

Your appointment has been successfully scheduled.

Details:
Date: {date}
Time: {time}
Doctor: {doctor}
Clinic: {config.CLINICNAME}

If you need to reschedule or cancel, please log in to your dashboard or call us.

Best regards,
{config.CLINICNAME} Team
"""
        self.send_email_async(recipient_email, subject, body)

    def send_appointment_update(self, recipient_email: str, user_name: str, new_date: str, new_time: str, new_status: str):
        subject = f"Appointment Update - {config.CLINICNAME}"
        body = f"""Dear {user_name},

Your appointment has been updated.

Status: {new_status}
New Date: {new_date}
New Time: {new_time}

Please check your dashboard for the latest details.

Best regards,
{config.CLINICNAME} Team
"""
        self.send_email_async(recipient_email, subject, body)

    def send_appointment_cancellation(self, recipient_email: str, user_name: str, date: str, time: str):
        subject = f"Appointment Cancelled - {config.CLINICNAME}"
        body = f"""Dear {user_name},

Your appointment scheduled for {date} at {time} has been cancelled.

If you did not request this cancellation, please contact us immediately.

Best regards,
{config.CLINICNAME} Team
"""
        self.send_email_async(recipient_email, subject, body)

email_service = EmailService()
