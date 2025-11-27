import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_service import chat_with_data

async def main():
    print("--- Testing Chat with Sources ---")
    
    query = "What has Test Subject been posting about?"
    print(f"Query: {query}")
    
    result = await chat_with_data(query)
    
    print("\nResponse:")
    print(result["response"][:200] + "...")
    
    print(f"\nSources Found: {len(result['sources'])}")
    for i, source in enumerate(result['sources']):
        print(f"\nSource {i+1} ({source['type']}):")
        print(f"Content: {source['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
