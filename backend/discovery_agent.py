import os
import requests
from typing import List

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_URL = "https://api.tavily.com/search"

async def search_for_topic(topic: str, max_results: int = 5) -> List[dict]:
    """
    Searches Tavily for a given topic and returns a list of results.
    """
    print(f"Discovery Agent: Searching Tavily for '{topic}'...")
    results = []
    
    if not TAVILY_API_KEY:
        print("ERROR: TAVILY_API_KEY not set. Skipping search.")
        return []

    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": topic,
            "search_depth": "basic", # or "advanced"
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False,
            "max_results": max_results,
        }
        
        response = requests.post(TAVILY_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for r in data.get("results", []):
            print(f"DEBUG: Found result: {r.get('title')}")
            results.append({
                "title": r.get('title'),
                "url": r.get('url'),
                "snippet": r.get('content') # Tavily uses 'content' for the snippet
            })
        print(f"DEBUG: Total results found: {len(results)}")
                
    except Exception as e:
        print(f"Discovery Agent Error: {e}")
        
    return results

async def discover_new_sources(topics: List[str]) -> List[dict]:
    """
    Iterates through topics and finds new sources.
    """
    all_findings = []
    for topic in topics:
        findings = await search_for_topic(topic)
        all_findings.extend(findings)
    return all_findings
