import asyncio
import uuid
from datetime import datetime
from .listening_service import listening_service
from .models import ListeningResult
from .database import get_db_connection

async def verify_listening_persistence():
    print("--- Verifying Listening Service Persistence ---")
    
    # 1. Manually insert a result via service logic (simulated)
    print("\n1. Testing Result Persistence...")
    
    # We need to simulate the DB insertion logic since _listen_loop is infinite
    # Let's manually insert into DB to test retrieval, or mock the connector.
    # Actually, let's just use the DB connection directly to insert a mock record 
    # and then use listening_service.get_latest_results() to retrieve it.
    
    mock_id = str(uuid.uuid4())
    mock_content = "This is a persistent listening result."
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO listening_results (id, source_platform, author, content, timestamp, matched_trend_id, matched_trend_topic, severity, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mock_id, "TestPlatform", "TestAuthor", mock_content, datetime.now().isoformat(), None, None, "Low", "http://test.com")
    )
    conn.commit()
    conn.close()
    
    # 2. Retrieve via Service
    results = listening_service.get_latest_results(limit=10)
    found_result = next((r for r in results if r.id == mock_id), None)
    
    if found_result:
        print(f"✅ Result retrieved via service: {found_result.content}")
    else:
        print("❌ Result NOT found via service!")

if __name__ == "__main__":
    asyncio.run(verify_listening_persistence())
