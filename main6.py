import requests
import stem.process
import psutil
import time
from fake_useragent import UserAgent

# Function to get the API endpoint from the user
def get_api_endpoint():
    return input("Enter the API endpoint URL: ")

# Function to start the Tor process
def start_tor():
    # Kill existing Tor processes on the specified port (e.g., 9051)
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if "tor.exe" in process.info['name']:
            try:
                process.kill()
            except psutil.NoSuchProcess:
                pass

    return stem.process.launch_tor_with_config(
        config={
            'SocksPort': '9050',  # Change the port to 9051 or another available port
        }
    )

# Function to make a Tor request with a random user agent
def make_tor_request(endpoint):
    try:
        user_agent = UserAgent().random  # Generate a new random user agent for each request
        with requests.Session() as session:
            session.proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
            headers = {'User-Agent': user_agent}  # Set the user agent in headers
            response = session.get(endpoint, headers=headers)
            response.raise_for_status()
            
            # Print the response content for debugging
            # print("Response Content:")
            # print(response.text)
            
            # Check if the response has content before parsing as JSON
            if response.text:
                try:
                    return response
                except ValueError:
                    print("Response does not contain valid JSON data.")
                    return None
            else:
                print("Response is empty.")
                return None
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None

# Main function
def main():
    api_endpoint = get_api_endpoint()  # Get the API endpoint from the user

    try:
        while True:
            tor_process = start_tor()
            response_data = make_tor_request(api_endpoint)
            if response_data:
                print("Response:", response_data)
            time.sleep(10)  # Sleep for 10 seconds between requests
    finally:
        tor_process.kill()  # Stop the Tor process when done

if __name__ == "__main__":
    main()
