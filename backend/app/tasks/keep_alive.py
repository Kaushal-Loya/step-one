import requests
import os
import sys

def ping_self():
    # Render automatically sets the RENDER_EXTERNAL_URL environment variable
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("RENDER_EXTERNAL_URL not set. Skipping ping.")
        return

    health_url = f"{url.rstrip('/')}/health"
    try:
        response = requests.get(health_url)
        if response.status_code == 200:
            print(f"Successfully pinged {health_url}")
        else:
            print(f"Ping failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error pinging {health_url}: {e}")

if __name__ == "__main__":
    ping_self()
