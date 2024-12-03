#import libraries
import requests

#function to check connection
def check_internet_connection():
    try:
        # Send a GET request to a reliable server (e.g., Google's public DNS)
        response = requests.get('http://www.google.com', timeout=5)

        # Check if the response status code indicates success
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError:
        return False

# Example usage
if check_internet_connection():
    print("Connected to the internet.")
else:
    print("No internet connection.")