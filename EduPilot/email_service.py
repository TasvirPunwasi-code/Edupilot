import os 
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_otp(receiver, otp):

    msg = EmailMessage()

    msg["Subject"] = "EduPilot Verification Code"
    msg["From"] = EMAIL
    msg["To"] = receiver

    msg.set_content(f"{otp} is your EduPilot verification code. Dont share your code with anyone.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)