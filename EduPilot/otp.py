# Imports Python's random module to generate random numbers
import random

# Creates a function that generates a 6-digit OTP verification code
def generate_otp():
    # Generates a random number between 100000 and 999999. Converts the number into a string and returns the OTP
    return str(random.randint(100000, 999999))
