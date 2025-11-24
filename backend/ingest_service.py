from .vector_store import add_documents, clear_collection
from .subjects import get_subjects
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
    
    # 1. Ingest Subjects
    subjects = await get_subjects()
    for s in subjects:
        # Create a descriptive string for the subject
        doc_text = f"Subject: {s.name}, Age: {s.age}, Risk Level: {s.risk_level}. Notes: {s.notes}"
        documents.append(doc_text)
        metadatas.append({"type": "subject", "id": str(s.id), "name": s.name})
        ids.append(f"subject_{s.id}")
        
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
        doc_text = f"Authority: {auth['name']}, Role: {auth['role']}, Relation: {auth['relation']} (Subject ID: {auth['subject_id']})."
        documents.append(doc_text)
        metadatas.append({"type": "authority", "name": auth['name'], "subject_id": auth['subject_id']})
        ids.append(f"authority_{auth['id']}")

    # Deduplicate documents based on IDs
    unique_docs = {}
    for i, doc_id in enumerate(ids):
        if doc_id not in unique_docs:
            unique_docs[doc_id] = {
                "document": documents[i],
                "metadata": metadatas[i],
                "id": doc_id
            }
    
    final_documents = [item["document"] for item in unique_docs.values()]
    final_metadatas = [item["metadata"] for item in unique_docs.values()]
    final_ids = [item["id"] for item in unique_docs.values()]

    if final_documents:
        add_documents(final_documents, final_metadatas, final_ids)
        print("Data ingestion complete.")
    else:
        print("No data to ingest.")
