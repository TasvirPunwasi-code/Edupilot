# Imports the os module to access email settings stored in environment variables
import os

# Imports the SMTP library used to send emails
import smtplib

# Imports EmailMessage to create and format the OTP email
from email.message import EmailMessage

# Imports load_dotenv to load variables from the .env file
from dotenv import load_dotenv

# Loads the environment variables from the .env file
load_dotenv()

# Gets the sender's email address from the environment variables
EMAIL = os.getenv("EMAIL_ADDRESS")

# Gets the Gmail app password from the environment variables
PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# Creates a function that sends an OTP verification code to a user's email
def send_otp(receiver, otp):
    # Creates a new email message
    msg = EmailMessage()

    # Sets the subject of the verification email
    msg["Subject"] = "EduPilot Verification Code"

    # Sets the sender's email address
    msg["From"] = EMAIL

    # Sets the email address that will receive the OTP
    msg["To"] = receiver

    # Creates the email message and inserts the generated OTP
    msg.set_content(
        f"{otp} is your EduPilot verification code. Dont share your code with anyone."
    )

    # Creates a secure connection to Gmail's SMTP server using SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        # Logs into the Gmail account using the email and app password
        smtp.login(EMAIL, PASSWORD)

        # Sends the completed OTP email to the receiver
        smtp.send_message(msg)
