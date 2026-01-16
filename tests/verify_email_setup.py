
import sys
import os
import asyncio
from loguru import logger

# Add backend to path to import config and services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from config import config
from services.email_service import email_service

async def test_email():
    print(f"--- Email Configuration Check ---")
    print(f"Server: {config.SMTPSERVER}")
    print(f"Port: {config.SMTPPORT}")
    print(f"Username: {config.SMTPUSERNAME}")
    print(f"Sender: {config.SENDEREMAIL}")
    print(f"Enabled: {config.ENABLEEMAILNOTIFICATIONS}")
    print(f"---------------------------------")

    if not config.ENABLEEMAILNOTIFICATIONS:
        logger.warning("Email notifications are disabled in .env (ENABLEEMAILNOTIFICATIONS=False)")
        return

    recipient = config.SENDEREMAIL # Send to self for testing
    print(f"\nAttempting to send test email to: {recipient}...")

    try:
        # We need to run the async wrapper or just call the sync method if available. 
        # The service uses threading for async, so we can just call it.
        # However, to see the error immediately, we should probably access the internal method or 
        # modify the service to return a future. 
        # For this test, we will replicate the logic of _send_email_thread to catch exceptions directly.
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = f"AI Medical Test <{config.SENDEREMAIL}>"
        msg['To'] = recipient
        msg['Subject'] = "MedPulse System Test: Email Configuration"
        
        body = "This is a test email from your AI Medical Receptionist system. If you see this, your SMTP configuration is correct!"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(config.SMTPSERVER, config.SMTPPORT)
        server.set_debuglevel(1) # Show SMTP interaction
        server.starttls()
        server.login(config.SMTPUSERNAME, config.SMTPPASSWORD)
        text = msg.as_string()
        server.sendmail(config.SENDEREMAIL, recipient, text)
        server.quit()
        
        print("\n✅ SUCCESS: Email sent successfully!")
        print(f"Check your inbox at {recipient}")
        
    except Exception as e:
        print(f"\n❌ FAILED: Could not send email.")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Google App Password.")
        print("2. Ensure 2-Step Verification is on.")
        print("3. Check firewall settings for port 587.")

if __name__ == "__main__":
    asyncio.run(test_email())
