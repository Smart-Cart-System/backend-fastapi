import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"  # Change to your server address

def add_item_to_cart(session_id, barcode, weight=None):
    """Test adding an item to cart"""
    try:
        # Prepare request data
        item_data = {
            "sessionID": int(session_id),
            "barcode": int(barcode)
        }
        
        # Add weight if provided
        if weight is not None:
            item_data["weight"] = float(weight)
        
        # Make API request
        url = f"{API_URL}/cart-items/add"
        print(f"Sending POST request to {url}")
        print(f"Request data: {json.dumps(item_data, indent=2)}")
        
        response = requests.post(url, json=item_data)
        
        # Process response
        if response.status_code == 200:
            item_data = response.json()
            print(f"Success! Item added to cart:")
            print(f"  Session ID: {item_data['session_id']}")
            print(f"  Item ID: {item_data['item_id']}")
            print(f"  Quantity: {item_data['quantity']}")
            
            if 'product' in item_data and item_data['product']:
                print(f"  Product: {item_data['product']['description']}")
                print(f"  Price: {item_data['product']['unit_price']}")
            
            if item_data.get('saved_weight'):
                print(f"  Weight: {item_data['saved_weight']}")
                
            return item_data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_add_item.py <session_id> <barcode> [weight]")
        sys.exit(1)
        
    session_id = sys.argv[1]
    barcode = sys.argv[2]
    weight = sys.argv[3] if len(sys.argv) > 3 else None
    
    add_item_to_cart(session_id, barcode, weight)