import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_listening_flow():
    print("1. Starting Listening Service...")
    try:
        resp = requests.post(f"{BASE_URL}/listening/start")
        if resp.status_code == 200:
            print("✅ Start request successful")
        else:
            print(f"❌ Start request failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print("2. Waiting for data (10s)...")
    time.sleep(10)

    print("3. Fetching Feed...")
    try:
        resp = requests.get(f"{BASE_URL}/listening/feed")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Feed fetched. Items: {len(data)}")
            if len(data) > 0:
                print(f"   Sample: {data[0]['content'][:50]}...")
            else:
                print("⚠️ Feed is empty. Connectors might be failing or slow.")
        else:
            print(f"❌ Feed request failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    print("4. Stopping Listening Service...")
    requests.post(f"{BASE_URL}/listening/stop")
    print("✅ Stopped.")

if __name__ == "__main__":
    test_listening_flow()
