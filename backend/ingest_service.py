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
        doc_text = f"Subject Profile: {s.name}, Age: {s.age}, Risk Level: {s.risk_level}. Notes: {s.notes}"
        documents.append(doc_text)
        metadatas.append({"type": "subject", "id": str(s.id), "name": s.name})
        ids.append(f"subject_{s.id}")
        
    # 2. Ingest Trends
    trends = await get_active_trends()
    for t in trends:
        doc_text = f"Disinformation Trend: {t.topic}, Severity: {t.severity}. Common Phrases: {', '.join(t.common_phrases)}"
        documents.append(doc_text)
        metadatas.append({"type": "trend", "topic": t.topic})
        ids.append(f"trend_{t.topic}")
        
    # Database connection for other entities
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # 3. Ingest Authorities
    cursor.execute("SELECT * FROM authorities")
    auth_rows = cursor.fetchall()

    for auth in auth_rows:
        doc_text = f"Trusted Authority for Subject {auth['subject_id']}: {auth['name']}, Role: {auth['role']}, Relation: {auth['relation']}."
        documents.append(doc_text)
        metadatas.append({"type": "authority", "name": auth['name'], "subject_id": auth['subject_id']})
        ids.append(f"authority_{auth['id']}")

    # 4. Ingest Social Media Posts (Digital Clone Data)
    cursor.execute("SELECT * FROM subject_social_posts ORDER BY posted_at DESC LIMIT 500") # Limit to recent 500 posts globally for now
    post_rows = cursor.fetchall()
    
    for post in post_rows:
        doc_text = f"Social Media Post by Subject {post['subject_id']} on {post['platform']}: {post['content']}"
        documents.append(doc_text)
        metadatas.append({
            "type": "social_post", 
            "subject_id": post['subject_id'], 
            "platform": post['platform'],
            "posted_at": post['posted_at'] or ""
        })
        ids.append(f"post_{post['id']}")

    # 5. Ingest Content Logs (Consumption History)
    cursor.execute("SELECT * FROM content_logs ORDER BY timestamp DESC LIMIT 200") # Limit to recent 200 logs
    log_rows = cursor.fetchall()
    
    for log in log_rows:
        doc_text = f"Content Consumed by Subject {log['subject_id']}: {log['content']}"
        documents.append(doc_text)
        metadatas.append({
            "type": "content_log", 
            "subject_id": log['subject_id'], 
            "timestamp": log['timestamp'] or ""
        })
        ids.append(f"log_{log['id']}")

    conn.close()

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
        print(f"Data ingestion complete. Ingested {len(final_documents)} items.")
    else:
        print("No data to ingest.")
