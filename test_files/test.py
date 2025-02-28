import requests
import json

# Replace with your API URL
api_url = "http://127.0.0.1:8000/products/scan-barcode"

# Replace with actual barcode scanned
barcode_data = {
    "barcode": "6223000110324",
    "cart_id": "cart123",
    "user_id": 1
}

# Send request to server
response = requests.post(api_url, json=barcode_data)

# Process response
if response.status_code == 200:
    product_data = response.json()
    print(f"Added {product_data['description']} to cart")
else:
    print(f"Error: {response.text}")