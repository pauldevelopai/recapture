import asyncio
import os
import sys
from discovery_agent import search_for_topic

async def verify_tavily():
    print("--- Verifying Tavily Integration ---")
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ Error: TAVILY_API_KEY environment variable is not set.")
        print("Please run with: TAVILY_API_KEY=your_key python3 backend/verify_tavily.py")
        return

    print(f"Using API Key: {api_key[:5]}...{api_key[-4:]}")
    
    topic = "latest disinformation trends 2024"
    print(f"Searching for: '{topic}'")
    
    try:
        results = await search_for_topic(topic, max_results=3)
        
        if results:
            print(f"✅ Success! Found {len(results)} results.")
            for i, res in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"Title: {res['title']}")
                print(f"URL: {res['url']}")
                print(f"Snippet: {res['snippet'][:100]}...")
        else:
            print("⚠️ No results found. Check your API key or quota.")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    asyncio.run(verify_tavily())
