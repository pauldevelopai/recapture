from .vector_store import add_documents, clear_collection
from .profiles import get_profiles
from .trend_monitor import get_active_trends
import asyncio

async def ingest_all_data():
    """
    Ingests all relevant application data into the vector store.
    """
    print("Starting data ingestion...")
    
    # Clear existing data to avoid duplicates (simple strategy for now)
    clear_collection()
    
    documents = []
    metadatas = []
    ids = []
    
    # 1. Ingest Profiles
    profiles = await get_profiles()
    for p in profiles:
        # Create a descriptive string for the profile
        doc_text = f"Profile: {p.name}, Age: {p.age}, Risk Level: {p.risk_level}. Notes: {p.notes}"
        documents.append(doc_text)
        metadatas.append({"type": "profile", "id": str(p.id), "name": p.name})
        ids.append(f"profile_{p.id}")
        
    # 2. Ingest Trends
    trends = await get_active_trends()
    for t in trends:
        doc_text = f"Trend: {t.topic}, Severity: {t.severity}. Common Phrases: {', '.join(t.common_phrases)}"
        documents.append(doc_text)
        metadatas.append({"type": "trend", "topic": t.topic})
        ids.append(f"trend_{t.topic}")
        
    # 3. Ingest Authorities
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM authorities")
    auth_rows = cursor.fetchall()
    conn.close()

    for auth in auth_rows:
        doc_text = f"Authority: {auth['name']}, Role: {auth['role']}, Relation: {auth['relation']} (Profile ID: {auth['profile_id']})."
        documents.append(doc_text)
        metadatas.append({"type": "authority", "name": auth['name'], "profile_id": auth['profile_id']})
        ids.append(f"authority_{auth['id']}")

    if documents:
        add_documents(documents, metadatas, ids)
        print("Data ingestion complete.")
    else:
        print("No data to ingest.")
