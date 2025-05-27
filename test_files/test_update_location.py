import requests
import json
import sys
import time

# Configuration
API_URL = ""  # Change to your server address
PI_API_KEY = ""  # API key from your .env file

def update_session_location(session_id, aisle_id):
    """Test updating a session's location when user moves to a new aisle"""
    try:
        # Prepare request data
        location_data = {
            "aisle_id": int(aisle_id)
        }
        
        # Prepare headers with API key
        headers = {
            "X-API-Key": PI_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Make API request
        url = f"{API_URL}/session-location/{session_id}"
        print(f"Sending PUT request to {url}")
        print(f"Request data: {json.dumps(location_data, indent=2)}")
        
        response = requests.put(url, json=location_data, headers=headers)
        
        # Process response
        if response.status_code == 200:
            location_data = response.json()
            print(f"Success! Session location updated:")
            print(f"  Session ID: {location_data['session_id']}")
            print(f"  Aisle ID: {location_data['aisle_id']}")
            print(f"  Created at: {location_data['created_at']}")
            print(f"  Updated at: {location_data['updated_at']}")
            return location_data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def simulate_walking_path(session_id, aisle_path, delay=5):
    """Simulate a user walking through multiple aisles with a delay between each"""
    print(f"Simulating path through aisles: {', '.join(map(str, aisle_path))}")
    
    for aisle_id in aisle_path:
        print(f"\nMoving to aisle {aisle_id}...")
        update_session_location(session_id, aisle_id)
        
        if aisle_id != aisle_path[-1]:  # Don't wait after the last aisle
            print(f"Waiting {delay} seconds before next movement...")
            time.sleep(delay)
    
    print("\nPath simulation complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Single update: python test_update_location.py <session_id> <aisle_id>")
        print("  Path simulation: python test_update_location.py <session_id> <aisle_id1> <aisle_id2> ... [delay]")
        print("Examples:")
        print("  python test_update_location.py 35 2")
        print("  python test_update_location.py 35 1 2 3 4 2")
        print("  python test_update_location.py 35 1 2 3 4 3")  # With aisles 1,2,3,4,3
        sys.exit(1)
        
    session_id = sys.argv[1]
    
    # Check if this is a path simulation or single update
    if len(sys.argv) > 3:
        # Get all aisle IDs from arguments
        aisle_path = [int(arg) for arg in sys.argv[2:-1] if arg.isdigit()]
        
        # Check if last argument is a delay value
        try:
            delay = int(sys.argv[-1])
            # If the last argument is a valid delay, don't include it in path
        except ValueError:
            # Last argument is another aisle ID
            aisle_path.append(int(sys.argv[-1]))
            delay = 5  # Default delay
            
        simulate_walking_path(session_id, aisle_path, delay)
    else:
        # Single update
        aisle_id = sys.argv[2]
        update_session_location(session_id, aisle_id)