import requests
import json
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"  # Change to your server address

def get_session_by_cart(cart_id):
    """Test getting an active session by cart ID"""
    try:
        # Make API request
        url = f"{API_URL}/customer-session/cart/{cart_id}"
        print(f"Sending GET request to {url}")
        
        response = requests.get(url)
        
        # Process response
        if response.status_code == 200:
            session_data = response.json()
            print(f"Success! Active session found:")
            print(f"  Session ID: {session_data['session_id']}")
            print(f"  User ID: {session_data['user_id']}")
            print(f"  Cart ID: {session_data['cart_id']}")
            print(f"  Created at: {session_data['created_at']}")
            return session_data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Use command line argument or default to cart ID 1
    cart_id = sys.argv[1] if len(sys.argv) > 1 else 1
    get_session_by_cart(cart_id)