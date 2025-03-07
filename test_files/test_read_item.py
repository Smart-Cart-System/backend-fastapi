import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"  # Change to your server address

def read_item(session_id, barcode):
    """Test reading an item with the barcode scanner"""
    try:
        # Prepare request data
        item_data = {
            "sessionID": int(session_id),
            "barcode": int(barcode)
        }
        
        # Make API request
        url = f"{API_URL}/items/read"
        print(f"Sending POST request to {url}")
        print(f"Request data: {json.dumps(item_data, indent=2)}")
        
        response = requests.post(url, json=item_data)
        
        # Process response
        if response.status_code == 200:
            product_data = response.json()
            print(f"Success! Item read:")
            print(f"  Item No: {product_data['item_no_']}")
            print(f"  Description: {product_data['description']}")
            print(f"  Arabic Description: {product_data['description_ar']}")
            print(f"  Size: {product_data['product_size']}")
            print(f"  Price: {product_data['unit_price']}")
            return product_data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_read_item.py <session_id> <barcode>")
        sys.exit(1)
        
    session_id = sys.argv[1]
    barcode = sys.argv[2]
    
    read_item(session_id, barcode)