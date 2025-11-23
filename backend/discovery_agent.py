from duckduckgo_search import DDGS
from typing import List
import asyncio

async def search_for_topic(topic: str, max_results: int = 5) -> List[dict]:
    """
    Searches DuckDuckGo for a given topic and returns a list of results.
    """
    print(f"Discovery Agent: Searching for '{topic}'...")
    results = []
    try:
        # DDGS is synchronous, so we run it in a thread if needed, 
        # but for simple usage in this async function we can call it directly 
        # or wrap in to_thread if it blocks too long.
        # Given the low volume, direct call is acceptable for MVP.
        with DDGS() as ddgs:
            # search for news or general results using 'html' backend to avoid strict rate limits
            search_results = ddgs.text(topic, max_results=max_results, backend="html")
            
            for r in search_results:
                print(f"DEBUG: Found result: {r.get('title')}")
                results.append({
                    "title": r.get('title'),
                    "url": r.get('href'),
                    "snippet": r.get('body')
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
