import os
from fastapi import APIRouter, Depends, HTTPException
from backend.app.dependencies import get_current_user
from backend.app.models import User
from backend.app.schema import PaymentRequest, PaymentResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies import get_db
from backend.app.models import Order, OrderStatus, Payment, OrderPayment
from sqlalchemy import select
from backend.app.daraja_integration import sendStkPush
import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter(tags=["Payment"], dependencies=[Depends(get_db)])

@router.post("/initiate_payment", response_model=PaymentResponse)
async def initiate_payment(
    payment_request: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user or current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You do not have permission to initiate payments.")
    try:
        orders = await db.execute(select(Order).where(Order.id == payment_request.order_id, Order.user_id == current_user.id))
        order = orders.scalars().first()
        if not order:            
            raise HTTPException(status_code=404, detail="Order not found or does not belong to the user.")
        
        if order.status != OrderStatus.PENDING.value or (
             order.payment_status != OrderPayment.PENDING and order.payment_status != OrderPayment.PENDING.value
       ):
            raise HTTPException(status_code=400, detail="Order is already paid.")

        if abs(payment_request.amount - order.total_price) > 0.01:
            raise HTTPException(status_code=400, detail="Payment amount does not match order total.")
        
        if not current_user.phone_number:
            raise HTTPException(status_code=400, detail="User phone number is required for payment.")
        
        stk_response = sendStkPush(
            phone_number=current_user.phone_number,
            amount=order.total_price,           
            order_id=order.id,
            callback_url=os.getenv("DARAJA_CALLBACK_URL"))
        

        if stk_response.get("ResponseCode")  == 0:
            transaction = Payment(
                order_id=order.id,
                checkout_request_id=stk_response.get("CheckoutRequestID"),
                merchant_request_id=stk_response.get("MerchantRequestID"),
                amount=payment_request.amount,
                phone_number=current_user.phone_number,
                status="initiated"
            )
            db.add(transaction) 
            
            order.mpesa_checkout_request_id = stk_response.get("CheckoutRequestID")
            order.payment_status = "processing"
            
            await db.commit()
            
            return PaymentResponse(
                success=True,
                message="Payment request sent to your phone. Please complete the transaction on your M-Pesa app.",
                checkout_request_id=stk_response.get("CheckoutRequestID"),
                merchant_request_id=stk_response.get("MerchantRequestID")
            )
        else:
            # STK push failed
            error_message = stk_response.get("errorMessage", "Failed to initiate payment")

            raise HTTPException(status_code=400, detail=f"Payment initiation failed: {error_message}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initiation error: {str(e)}")

# @router.post("/api/payments/callback")
# async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
#     """
#     Handle M-Pesa payment callback from Daraja API
    
#     This endpoint receives payment confirmation from Safaricom
#     and updates order/transaction status accordingly
#     """
#     try:
#         data = await request.json()
#         body = data.get("Body", {})
#         stk_callback = body.get("stkCallback", {})
        
#         checkout_request_id = stk_callback.get("CheckoutRequestID")
#         result_code = stk_callback.get("ResultCode")
#         result_desc = stk_callback.get("ResultDesc", "")
        
#         # Find the transaction
#         transaction = db.query(Payment).filter(
#             Payment.checkout_request_id == checkout_request_id
#         ).first()
        
#         if not transaction:
#             return {"ResultDesc": "Transaction not found", "ResultCode": 1}
        
#         # Find the associated order
#         order = db.query(Order).filter(Order.id == transaction.order_id).first()
        
#         if result_code == 0:
#             # Payment successful
#             callback_metadata = stk_callback.get("CallbackMetadata", {})
#             items = callback_metadata.get("Item", [])
            
#             # Extract transaction details
#             mpesa_receipt_number = None           
            
#             for item in items:
#                 name = item.get("Name")
#                 if name == "MpesaReceiptNumber":
#                     mpesa_receipt_number = item.get("Value")
#                 elif name == "TransactionDate":
#                     transaction_date = item.get("Value")
#                 elif name == "PhoneNumber":
#                     phone_number = item.get("Value")
            
#             # Update transaction
#             transaction.transaction_id = mpesa_receipt_number
#             transaction.result_code = result_code
#             transaction.result_desc = result_desc
#             transaction.status = "completed"
            
#             # Update order
#             if order:
#                 order.payment_status = "paid"
#                 order.status = "processing"  # Move to next stage
#                 order.mpesa_transaction_id = mpesa_receipt_number
#                 order.updated_at = datetime.utcnow()
            
#             db.commit()
            
#             # Send confirmation email (background task)
#             if order:
#                 # background_tasks.add_task(send_payment_confirmation_email, order.user_id, order.id)
#                 pass
            
#             return {"ResultDesc": "Payment processed successfully", "ResultCode": 0}
            
#         else:
#             # Payment failed or cancelled
#             transaction.result_code = result_code
#             transaction.result_desc = result_desc
#             transaction.status = "failed"
            
#             if order:
#                 order.payment_status = "failed"
#                 order.updated_at = datetime.utcnow()
            
#             db.commit()
            
#             return {"ResultDesc": "Payment failed", "ResultCode": 0}
            
#     except Exception as e:
#         print(f"Callback processing error: {str(e)}")
#         return {"ResultDesc": "Callback processing error", "ResultCode": 1}

# @router.get("/api/payments/status/{order_id}")
# async def check_payment_status(
#     order_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Check payment status for a specific order
#     Only allows users to check their own orders
#     """
#     try:
#         # Verify order belongs to current user
#         order = db.query(Order).filter(
#             Order.id == order_id,
#             Order.user_id == current_user.id
#         ).first()
        
#         if not order:
#             raise HTTPException(status_code=404, detail="Order not found")
        
#         # Get transaction details
#         transaction = db.query(Payment).filter(
#             Payment.order_id == order_id
#         ).first()
        
#         # If we have a checkout request ID, query Daraja for latest status
#         if order.mpesa_checkout_request_id and transaction and transaction.status == "initiated":
#             try:
#                 stk_status = daraja.query_transaction_status(order.mpesa_checkout_request_id)
                
#                 # Update status based on query result
#                 if stk_status.get("ResultCode") == "0":
#                     # Check if payment was completed
#                     if stk_status.get("ResultDesc") == "The service request has been accepted successfully":
#                         # Payment might still be pending
#                         pass
#                     else:
#                         # Update transaction status
#                         transaction.result_desc = stk_status.get("ResultDesc")
#                         db.commit()
                        
#             except Exception as e:
#                 print(f"Error querying STK status: {str(e)}")
        
#         return {
#             "order_id": order.id,
#             "payment_status": order.payment_status,
#             "order_status": order.status,
#             "transaction_id": order.mpesa_transaction_id,
#             "amount": float(order.total_price),
#             "created_at": order.created_at,
#             "updated_at": order.updated_at
#         }
               
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error checking payment status: {str(e)}")