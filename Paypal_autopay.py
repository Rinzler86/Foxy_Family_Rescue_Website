import requests
from ignore_file import PAYPAL_SECRET, PAYPAL_CLIENT

# Request for the access token
auth_response = requests.post('https://api.sandbox.paypal.com/v1/oauth2/token',
                              headers={
                                  'Accept': 'application/json',
                                  'Accept-Language': 'en_US',
                              },
                              data={
                                  'grant_type': 'client_credentials'
                              },
                              auth=(PAYPAL_CLIENT, PAYPAL_SECRET), timeout=60)  # your client id and secret key

# Get the access token from the response
access_token = auth_response.json()['access_token']

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    'PayPal-Request-Id': 'PRODUCT-18062019-001',
    'Prefer': 'return=representation',
}

product_data = {
    "name": "Video Streaming Service",
    "description": "Video streaming service",
    "type": "SERVICE",
    "category": "SOFTWARE",
    "image_url": "https://example.com/streaming.jpg",
    "home_url": "https://example.com/home"
}

# Make a POST request to create a product
response = requests.post('https://api.sandbox.paypal.com/v1/catalogs/products', headers=headers, json=product_data, timeout=60)

product_id = response.json()['id']  # Get the product id from the response

# Define the plan details
plan_data = {
    "product_id": product_id,
    "name": "Video Streaming Plan",
    "description": "Monthly subscription to the video streaming service",
    "status": "ACTIVE",
    "billing_cycles": [
        {
            "frequency": {
                "interval_unit": "MONTH",
                "interval_count": 1
            },
            "tenure_type": "REGULAR",
            "sequence": 1,
            "total_cycles": 0,
            "pricing_scheme": {
                "fixed_price": {
                    "value": "10",
                    "currency_code": "USD"
                }
            }
        }
    ],
    "payment_preferences": {
        "auto_bill_outstanding": True,
        "setup_fee_failure_action": "CONTINUE",
        "payment_failure_threshold": 3
    }
}

# Create the plan
response = requests.post('https://api.sandbox.paypal.com/v1/billing/plans', headers=headers, json=plan_data, timeout=60)

print(response.json())
