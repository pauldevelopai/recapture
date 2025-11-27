import asyncio
import sys
import os
import uuid
import requests

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://127.0.0.1:8000/api"

def main():
    print("--- Testing Subject Update Endpoint ---")
    
    # 1. Create a dummy subject
    subject_id = str(uuid.uuid4())
    subject_data = {
        "id": subject_id,
        "name": "Test Update Subject",
        "age": 25,
        "risk_level": "Low",
        "notes": "Original notes"
    }
    
    try:
        # Create
        print("Creating subject...")
        res = requests.post(f"{API_URL}/subjects", json=subject_data)
        if res.status_code != 200:
            print(f"FAILED to create subject: {res.text}")
            return
            
        print("Subject created.")
        
        # 2. Update notes
        print("Updating notes...")
        subject_data['notes'] = "Updated notes via API"
        res = requests.put(f"{API_URL}/subjects/{subject_id}", json=subject_data)
        
        if res.status_code == 200:
            updated_subject = res.json()
            if updated_subject['notes'] == "Updated notes via API":
                print("SUCCESS: Notes updated correctly.")
            else:
                print(f"FAILURE: Notes not updated. Got: {updated_subject['notes']}")
        else:
            print(f"FAILURE: Update request failed: {res.text}")
            
    except Exception as e:
        print(f"FAILURE: Exception raised: {e}")
        
    # Cleanup (optional, but good practice if we had a delete endpoint exposed easily)

if __name__ == "__main__":
    main()
