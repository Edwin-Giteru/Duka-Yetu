import requests
import os
import base64
import json
from datetime import datetime

CONSUMER_KEY = os.getenv("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("DARAJA_CONSUMER_SECRET")
URL =os.getenv("DARAJA_BASE_URL")
short_code = os.getenv("DARAJA_SHORT_CODE")
passkey = os.getenv("DARAJA_PASSKEY")


def generate_timestamp():
    """
    Generates a timestamp in the format YYYYMMDDHHMMSS.
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")

def generate_password():
    """
    Generates a password for the STK push request.
    The password is a base64 encoded string of the short code, passkey, and timestamp.
    """
    timestamp = generate_timestamp()
    password = f"{short_code}{passkey}{timestamp}"
    return base64.b64encode(password.encode()).decode()

def generate_access_token():
    """"
    Generates access token for daraja API.
    """
    api_url =f"{URL}/oauth/v1/generate?grant_type=client_credentials"

    try:
        encode_credentials = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()

        headers = {
            "Authorization": f"Basic{encode_credentials}",
            "Content-Type": "application/json"
        }

        response = requests.get(api_url, headers=headers).json()

        if "access_token" in response:
            return response["access_token"]
        else:
            raise Exception("Failed to get access token: " + json.dumps(response))
        
    except Exception as e:
        raise Exception(f"Error generating access token: {str(e)}")
    

def sendStkPush(phone_number: str, amount: float, order_id: int, callback_url: str):

    """
    Sends an STK push request to the Daraja API.
    """
    
    api_url = f"{URL}/mpesa/stkpush/v1/processrequest"
    access_token = generate_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": short_code,
        "Password": generate_password(),
        "Timestamp": generate_timestamp(),
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": 1,  # Example amount
        "PartyA": "2540707913754",  # Example phone number
        "PartyB": short_code,
        "PhoneNumber": "254707913754",  # Example phone number
        "CallBackURL": f"{URL}/callback",
        "AccountReference": "Test123",
        "TransactionDesc": "Payment for testing"
    }

    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"STK Push failed: {response.text}")    