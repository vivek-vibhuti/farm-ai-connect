import requests
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

def send_whatsapp_notification(phone, message, voice_url=None):
    """
    Send WhatsApp notification using Twilio
    
    Setup: 
    1. Sign up at twilio.com
    2. Get WhatsApp sandbox or production number
    3. Add credentials to .env
    """
    
    if not TWILIO_ACCOUNT_SID:
        print("Twilio not configured. Skipping WhatsApp notification.")
        return False
    
    # Format phone number
    if not phone.startswith("whatsapp:"):
        phone = f"whatsapp:+91{phone}"  # Assuming Indian numbers
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    data = {
        "From": TWILIO_WHATSAPP_NUMBER,
        "To": phone,
        "Body": message
    }
    
    # Add audio if available
    if voice_url:
        data["MediaUrl"] = voice_url
    
    try:
        response = requests.post(
            url,
            data=data,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        )
        
        if response.status_code == 201:
            print(f"WhatsApp sent to {phone}")
            return True
        else:
            print(f"WhatsApp failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"WhatsApp error: {e}")
        return False
