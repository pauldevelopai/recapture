import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.ingest_service import ingest_all_data
from backend.rag_service import retrieve_context
from backend.vector_store import get_collection_stats

async def main():
    print("--- Testing RAG Integration ---")
    
    # 1. Test Ingestion
    print("\n1. Running Ingestion...")
    await ingest_all_data()
    
    stats = get_collection_stats()
    print(f"Collection Stats: {stats}")
    
    # 2. Test Query
    print("\n2. Testing Query...")
    # Query for a subject if one exists, otherwise generic
    query = "Information about subject Test Subject, their authorities, and recent content consumption"
    context = await retrieve_context(query)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved Context Length: {len(context)}")
    print(f"Retrieved Context Preview:\n{context[:500]}...")
    
    if "Social Media Post" in context or "Content Consumed" in context:
        print("\nSUCCESS: Found new data types in context!")
    else:
        print("\nWARNING: Did not find new data types in context (might be expected if DB is empty)")

if __name__ == "__main__":
    asyncio.run(main())
