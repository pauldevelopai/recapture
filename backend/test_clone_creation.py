import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.digital_clone_service import get_or_create_clone
from backend.database import get_db_connection

async def main():
    print("--- Testing Clone Creation Flow ---")
    
    # 1. Create a dummy subject with NO posts
    conn = get_db_connection()
    cursor = conn.cursor()
    subject_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO subjects (id, name, age, risk_level, notes) VALUES (?, ?, ?, ?, ?)",
        (subject_id, "Test No Posts", 20, "Low", "Testing clone creation")
    )
    conn.commit()
    conn.close()
    
    print(f"Created test subject: {subject_id}")
    
    try:
        # 2. Try to get/create clone
        print("Attempting to create clone...")
        clone = await get_or_create_clone(subject_id)
        
        print(f"Clone created successfully!")
        print(f"Clone ID: {clone.id}")
        print(f"Status: {clone.status}")
        
        if clone.status == 'pending':
            print("SUCCESS: Clone is in pending status as expected.")
        else:
            print(f"FAILURE: Clone status is {clone.status}, expected 'pending'.")
            
    except Exception as e:
        print(f"FAILURE: Exception raised: {e}")
    finally:
        # Cleanup
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        cursor.execute("DELETE FROM digital_clones WHERE subject_id = ?", (subject_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
