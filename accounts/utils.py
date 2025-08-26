# accounts/utils.py
import random, string
from django.conf import settings
from .models import SiteConfig

def generate_token():
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=3))
    return letters + numbers

def send_login_token(email, token):
    config = SiteConfig.get_config()

    if not config.mailjet_api_key or not config.mailjet_api_secret:
        # Development fallback
        if settings.DEBUG:
            print(f"[DEV MODE] Login token for {email}: {token}")
            return True
        else:
            raise Exception("Mailjet API keys are not configured in SiteConfig.")

    from mailjet_rest import Client
    mailjet = Client(auth=(config.mailjet_api_key, config.mailjet_api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {"Email": config.from_email, "Name": "Smart Classroom Booking"},
                "To": [{"Email": email}],
                "Subject": "Your Login Code",
                "TextPart": f"Your login code is {token}. It is valid for {config.token_expiry_minutes} minutes.",
            }
        ]
    }
    return mailjet.send.create(data=data)
