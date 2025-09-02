# accounts/utils.py
import random
from django.core.mail import send_mail
from django.conf import settings
import random
from mailjet_rest import Client
from django.conf import settings
from .models import SystemConfig

def generate_token():
    letters = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
    digits  = ''.join(random.choices("0123456789", k=3))
    return f"{letters}{digits}"

def send_login_token(email: str, token: str):
    cfg = SystemConfig.latest_enabled()  # <-- use this
    if not cfg or not cfg.mailjet_api_key or not cfg.mailjet_secret_key or not cfg.sender_email:
        print(f"[DEV] Token for {email}: {token}")
        return True

    mj = Client(auth=(cfg.mailjet_api_key, cfg.mailjet_secret_key), version="v3.1")
    data = {
        "Messages": [{
            "From": {"Email": cfg.sender_email, "Name": "Smart Classroom Booking"},
            "To": [{"Email": email}],
            "Subject": "Your Login Code",
            "TextPart": f"Your login code is {token}. It will expire in {cfg.token_expiry_minutes} minutes."
        }]
    }
    resp = mj.send.create(data=data)
    return resp.status_code in (200, 201)
