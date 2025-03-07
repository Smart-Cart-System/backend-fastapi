import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"  # Change to your server address

def remove_item_from_cart(session_id, barcode):
    """Test removing an item from the cart"""
    try:
        # Prepare request data
        item_data = {
            "sessionID": int(session_id),
            "barcode": int(barcode)
        }
        
        # Make API request
        url = f"{API_URL}/cart-items/remove"
        print(f"Sending DELETE request to {url}")
        print(f"Request data: {json.dumps(item_data, indent=2)}")
        
        response = requests.delete(url, json=item_data)
        
        # Process response
        if response.status_code == 200:
            result = response.json()
            print(f"Success! {result['message']}")
            
            if result.get('item'):
                print(f"  Session ID: {result['item']['session_id']}")
                print(f"  Item ID: {result['item']['item_id']}")
                print(f"  New Quantity: {result['item']['quantity']}")
                
                if result['item'].get('product'):
                    print(f"  Product: {result['item']['product']['description']}")
            
            return result
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_remove_item.py <session_id> <barcode>")
        sys.exit(1)
        
    session_id = sys.argv[1]
    barcode = sys.argv[2]
    
    remove_item_from_cart(session_id, barcode)