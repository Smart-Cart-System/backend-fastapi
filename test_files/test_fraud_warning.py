import requests
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"  # Change to your server address

def report_fraud_warning(session_id, warning_type):
    """Report a fraud warning"""
    try:
        # Prepare request data
        warning_data = {
            "session_id": int(session_id),
            "type_of_warning": warning_type
        }
        
        # Make API request
        url = f"{API_URL}/fraud-warnings/"
        print(f"Reporting fraud warning to {url}")
        print(f"Warning type: {warning_type}")
        
        response = requests.post(url, json=warning_data)
        
        # Process response
        if response.status_code == 200:
            warning_data = response.json()
            print(f"Success! Warning reported (ID: {warning_data['id']})")
            return warning_data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_fraud_warning.py <session_id> <warning_type>")
        print("Example warning types: \"weight increased\", \"weight decreased\"")
        sys.exit(1)
        
    session_id = sys.argv[1]
    warning_type = sys.argv[2]
    
    report_fraud_warning(session_id, warning_type)