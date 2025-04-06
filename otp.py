import os
import random
import time
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

otp_store = {}

def send_otp_sms(phone):
    otp = str(random.randint(100000, 999999))
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        body=f"Your OTP for DeFi Loan Platform is: {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )

    otp_store[phone] = {"otp": otp, "timestamp": time.time()}
    print(f"OTP sent to {phone}: {otp}")  

def verify_otp(phone, entered_otp):
    otp_data = otp_store.get(phone)
    if not otp_data:
        return False

    if time.time() - otp_data["timestamp"] > 300:
        del otp_store[phone]
        return False

    if otp_data["otp"] == entered_otp:
        del otp_store[phone]
        return True

    return False
