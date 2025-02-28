import requests
import json

api_url = "https://smartcart.up.railway.app/products/scan-barcode"

barcode_data = {
    "barcode": "6223000110324",
    "cart_id": "cart123",
    "user_id": 1
}

response = requests.post(api_url, json=barcode_data)

if response.status_code == 200:
    product_data = response.json()
    print(f"Added {product_data['description']} to cart")
else:
    print(f"Error: {response.text}")