import requests
import json
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Airflow configuration
AIRFLOW_URL = "https://airflow.ducttdevops.com"
USERNAME = "admin"
PASSWORD = "admin"

# Try different token endpoints
endpoints = [
    "/api/v1/security/login",
    "/auth/token", 
    "/api/auth/token",
]

print("Trying to get JWT token from Airflow...")
print(f"URL: {AIRFLOW_URL}")
print(f"Username: {USERNAME}\n")

for endpoint in endpoints:
    try:
        print(f"Trying endpoint: {endpoint}")
        response = requests.post(
            f"{AIRFLOW_URL}{endpoint}",
            json={"username": USERNAME, "password": PASSWORD},
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                token = data["access_token"]
                print(f"\n✓ Success! JWT Token obtained from {endpoint}")
                print(f"\nToken: {token}")
                print(f"\nAdd this to your .env file:")
                print(f"AIRFLOW_JWT_TOKEN={token}")
                break
            elif "token" in data:
                token = data["token"]
                print(f"\n✓ Success! JWT Token obtained from {endpoint}")
                print(f"\nToken: {token}")
                print(f"\nAdd this to your .env file:")
                print(f"AIRFLOW_JWT_TOKEN={token}")
                break
        else:
            print(f"  Status: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n\nNote: If none worked, your Airflow might not support JWT tokens.")
print("In that case, use basic auth with the original mcp-server-apache-airflow.")
