import os
import paypalrestsdk
from fastapi import HTTPException

# ================================================
# 💰 PayPal SDK Configuration
# ================================================
# Configure the SDK using environment variables
try:
    paypalrestsdk.configure({
        "mode": os.getenv("PAYPAL_MODE", "live"),  # "sandbox" for testing, "live" for production
        "client_id": os.getenv("PAYPAL_CLIENT_ID"),
        "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
    })
    print("✅ PayPal SDK configured successfully.")
except Exception as e:
    print(f"❌ Failed to configure PayPal SDK: {e}")


# ================================================
# 💳 Create PayPal Payment Order
# ================================================
def create_paypal_order():
    """
    Creates a PayPal payment order and returns the approval URL.
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "ntube://payment/success",
            "cancel_url": "ntube://payment/cancel"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "NTUBE PRO Subscription",
                    "sku": "NTUBE-PRO-001",
                    "price": "5.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "5.00",
                "currency": "USD"
            },
            "description": "One-time payment for NTUBE PRO Subscription."
        }]
    })

    # Create the payment and get the approval URL
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return str(link.href)
        # If no approval URL is found after successful creation
        raise HTTPException(status_code=500, detail="Could not find PayPal approval URL.")
    else:
        # If payment creation fails
        print(f"❌ PayPal Payment Error: {payment.error}")
        raise HTTPException(status_code=500, detail=str(payment.error))
