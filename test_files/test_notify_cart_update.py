import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"  # Change to your server address

def notify_cart_update(session_id, barcode=0):
    """Test sending a cart-update notification via WebSocket"""
    try:
        # Prepare request data
        notification_data = {
            "session_id": int(session_id),
            "barcode": int(barcode)
        }
        
        # Make API request
        url = f"{API_URL}/fraud-warnings/notify-cart-update"
        print(f"Sending POST request to {url}")
        print(f"Request data: {json.dumps(notification_data, indent=2)}")
        
        response = requests.post(url, json=notification_data)
        
        # Process response
        if response.status_code == 200:
            result = response.json()
            print(f"Success! {result['message']}")
            print(f"WebSocket notification sent to session ID: {session_id}")
            print(f"Message type: cart-updated")
            print(f"Barcode: {barcode}")
            return result
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_notify_cart_update.py <session_id> [barcode]")
        print("Example: python test_notify_cart_update.py 1 6223000110324")
        sys.exit(1)
        
    session_id = sys.argv[1]
    barcode = sys.argv[2] if len(sys.argv) > 2 else 0
    
    notify_cart_update(session_id, barcode)