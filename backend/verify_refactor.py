import requests
import sys
import os

port = sys.argv[1] if len(sys.argv) > 1 else "8000"
BASE_URL = f"http://localhost:{port}/api"

def test_subject_flow():
    import uuid
    subject_id = f"test-subject-{uuid.uuid4().hex[:8]}"
    print(f"1. Creating a new Subject ({subject_id})...")
    subject_data = {
        "id": subject_id,
        "name": "Alex Test",
        "age": 16,
        "risk_level": "Medium",
        "notes": "Testing digital clone."
    }
    try:
        resp = requests.post(f"{BASE_URL}/subjects", json=subject_data)
        if resp.status_code == 200:
            print("✅ Subject created successfully")
        else:
            print(f"❌ Failed to create subject: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print("2. Fetching Subjects...")
    try:
        resp = requests.get(f"{BASE_URL}/subjects")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Fetched {len(data)} subjects")
            found = any(s['id'] == subject_id for s in data)
            if found:
                print("✅ Created subject found in list")
            else:
                print("❌ Created subject NOT found in list")
        else:
            print(f"❌ Failed to fetch subjects: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    print("3. Adding Authority...")
    auth_data = {
        "name": "Father John",
        "role": "Priest",
        "relation": "Confidant"
    }
    try:
        resp = requests.post(f"{BASE_URL}/subjects/{subject_id}/authorities", json=auth_data)
        if resp.status_code == 200:
            print("✅ Authority added successfully")
        else:
            print(f"❌ Failed to add authority: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    print("4. Testing Digital Clone Simulation (AI)...")
    # This might fail if OpenAI key is not set, but we check endpoint existence
    # We need to call generate-argument which uses the subject data
    arg_req = {
        "context": "The earth is flat",
        "profile_id": subject_id
    }
    try:
        resp = requests.post(f"{BASE_URL}/generate-argument", json=arg_req)
        if resp.status_code == 200:
            print("✅ Argument generation (with Subject context) successful")
            print(f"Response snippet: {resp.json()['argument_text'][:50]}...")
        else:
            print(f"⚠️ Argument generation failed (might be expected if no OpenAI key): {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_subject_flow()
