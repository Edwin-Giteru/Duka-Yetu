import os
import base64
from re import S
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time

class DarajaAPI:
    def __init__(self):
        self.consumer_key= os.getenv("DARAJA_CONSUMER_KEY")
        self.consumer_secret = os.getenv("DARAJA_CONSUMER_SECRET")
        self.passkey = os.getenv("DARAJA_PASSKEY")
        self.business_shortcode = os.getenv("DARAJA_BUSINESS_SHORTCODE")
        self.base_url= os.getenv("DARAJA_BASE_URL", "https://sandbox.safaricom.co.ke")
        self.callback = os.getenv("DARAJA_CALLBACK_URL")
        self.access_token = None
        self.token_expires_at = None

    def get_access_token(self) -> str:
        try:
             #    check if current token is still valid
            if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
                return self.access_token
             
            #  create credentials for authentication
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                expires_in = int(data.get("expires_in", 3600)) - 300
                self.token_expires_at = datetime.now().timestamp() + expires_in
                return self.access_token
            
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get access token: {response.text}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while getting access token: {str(e)}"
            )
    def generate_password(self) -> tuple:
        try:
            if not os.getenv("DARAJA_BUSINESS_SHORT_CODE")or not os.getenv("DARAJA_PASS_KEY"):
                raise HTTPException(
                    status_code=400,
                    detail="Business Shortcode and Passkey must be set in environment variables"
                )
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(
                f"{os.getenv("DARAJA_BUSINESS_SHORT_CODE")}{os.getenv("DARAJA_PASS_KEY")}{timestamp}".encode()
            ).decode()
            return password, timestamp
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while generating password: {str(e)}"
            )
    
    def initiate_stk_push(self, phone_number: str, amount: float, callback_url: str, order_id: int) -> Dict[str, Any]:
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # format the phone number to start with '254'
            if not phone_number.startswith("254"):
                if phone_number.startswith("0"):
                    phone_number = "254" + phone_number[1:]
                else:
                    phone_number = "254" + phone_number
            if len(phone_number) < 12:
                raise HTTPException(
                    status_code=400,
                    detail="Phone number must be at least 12 digits long"
                )

            payload = {
                "BusinessShortCode": 174379,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerBuyGoodsOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": 174379,
                "PhoneNumber": phone_number,
                "CallBackURL": os.getenv("DARAJA_CALLBACK_URL", callback_url),
                "IdentifierType":"2",
                "AccountReference": "DukaYetu Account",
                "TransactionDesc": "Payment for Order #{order_id}".format(order_id=order_id)
            }

            response = requests.post(
                f"{os.getenv("DARAJA_BASE_URL")}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to initiate STK push: {response.text}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while initiating STK push: {str(e)}"
            )
    def query_transaction_status(self, checkout_request_id: str) -> Dict[str, Any]:
        try:
            access_token = self.get_access_token()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "Initiator": "testapi",
                "SecurityCredential": self.passkey,
                "CommandID": "TransactionStatusQuery",
                "TransactionID": checkout_request_id,
                "PartyA": self.business_shortcode,
                "IdentifierType": "4",  # 4 for MSISDN
                "ResultURL": f"{self.base_url}/mpesa/result",
                "QueueTimeOutURL": f"{self.base_url}/mpesa/timeout",
                "Remarks": "Transaction status query"
            }

            response = requests.post(
                f"{self.base_url}/mpesa/transactionstatus/v1/query",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to query transaction status: {response.text}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while querying transaction status: {str(e)}"
            )