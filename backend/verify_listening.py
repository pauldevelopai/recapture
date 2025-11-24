import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_listening_service():
    print("Testing Deep Listening Service...")

    # 1. Start Listening
    try:
        print("1. Starting listening service...")
        response = requests.post(f"{BASE_URL}/listening/start")
        response.raise_for_status()
        print("   ✅ Service started.")
    except Exception as e:
        print(f"   ❌ Failed to start service: {e}")
        return

    # 2. Wait for data generation
    print("2. Waiting for data generation (5 seconds)...")
    time.sleep(5)

    # 3. Fetch Feed
    try:
        print("3. Fetching listening feed...")
        response = requests.get(f"{BASE_URL}/listening/feed")
        response.raise_for_status()
        data = response.json()
        print(f"   ✅ Fetched {len(data)} items.")
        
        threats = [item for item in data if item.get('matched_trend_id')]
        print(f"   ℹ️  Detected {len(threats)} threats.")
        
        if len(data) > 0:
            print("   Example item:")
            print(f"   - Platform: {data[0]['source_platform']}")
            print(f"   - Content: {data[0]['content']}")
            print(f"   - Threat: {data[0].get('matched_trend_topic', 'None')}")
            
    except Exception as e:
        print(f"   ❌ Failed to fetch feed: {e}")

    # 4. Stop Listening
    try:
        print("4. Stopping listening service...")
        response = requests.post(f"{BASE_URL}/listening/stop")
        response.raise_for_status()
        print("   ✅ Service stopped.")
    except Exception as e:
        print(f"   ❌ Failed to stop service: {e}")

if __name__ == "__main__":
    test_listening_service()
