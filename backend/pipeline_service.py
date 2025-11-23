import uuid
from datetime import datetime
from typing import List
from .models import Source, RawContent
from .ai_service import analyze_text
from .database import get_db_connection
import requests
from bs4 import BeautifulSoup

# In-memory storage for demo (replace with DB in production)
SOURCES = []
RAW_CONTENT = []

async def get_sources() -> List[Source]:
    return SOURCES

async def add_source(source: Source) -> Source:
    if not source.id:
        source.id = str(uuid.uuid4())
    SOURCES.append(source)
    return source

async def delete_source(source_id: str):
    global SOURCES
    SOURCES = [s for s in SOURCES if s.id != source_id]

async def get_raw_content() -> List[RawContent]:
    return sorted(RAW_CONTENT, key=lambda x: x.timestamp or "", reverse=True)

async def approve_content(content_id: str):
    for content in RAW_CONTENT:
        if content.id == content_id:
            content.status = "approved"
            break

async def discard_content(content_id: str):
    for content in RAW_CONTENT:
        if content.id == content_id:
            content.status = "discarded"
            break

from .discovery_agent import discover_new_sources

# In-memory topics for demo
MONITORED_TOPICS = []

async def add_topic(topic: str):
    if topic not in MONITORED_TOPICS:
        MONITORED_TOPICS.append(topic)

async def get_topics():
    return MONITORED_TOPICS

async def run_pipeline():
    """
    Trigger the pipeline: Discover -> Fetch -> Process -> Curate
    """
    print("Running Threat Intel Pipeline...")
    new_content_count = 0
    
    # 0. Discover New Sources via Agents
    if MONITORED_TOPICS:
        print(f"Discovering content for topics: {MONITORED_TOPICS}")
        discovered_items = await discover_new_sources(MONITORED_TOPICS)
        print(f"DEBUG: Discovered {len(discovered_items)} items.")
        for item in discovered_items:
             # Create a temporary source for the discovered item if needed, 
             # or just process it directly as a "Discovered" source type.
             # For MVP, we'll treat them as direct items to process.
             try:
                if any(c.url == item['url'] for c in RAW_CONTENT):
                    continue

                # Process Discovered Item
                # We might need to fetch the full content if the snippet isn't enough,
                # but often the snippet + title is enough for initial triage.
                # Let's try to fetch the full page if possible, else use snippet.
                
                content_text = item['snippet']
                # Optional: Deep fetch
                # fetched = await fetch_from_url(item['url'])
                # if fetched: content_text = fetched
                
                analysis = await analyze_text(content_text[:2000])
                
                status = "pending"
                if analysis.radicalization_score < 0.1:
                    status = "discarded"

                raw = RawContent(
                    id=str(uuid.uuid4()),
                    source_id="discovery_agent", # Virtual source
                    content=f"Title: {item['title']}\n\n{content_text}",
                    url=item['url'],
                    timestamp=datetime.now().isoformat(),
                    status=status,
                    analysis_summary=analysis.summary,
                    risk_score=analysis.radicalization_score
                )
                RAW_CONTENT.append(raw)
                new_content_count += 1
             except Exception as e:
                 print(f"Error processing discovered item {item['url']}: {e}")

    # 1. Fetch from Manual Sources
    for source in SOURCES:
        try:
            fetched_items = await fetch_from_source(source)
            
            for item in fetched_items:
                if any(c.url == item['url'] for c in RAW_CONTENT):
                    continue
                
                analysis = await analyze_text(item['content'][:2000])
                
                status = "pending"
                if analysis.radicalization_score < 0.1:
                    status = "discarded"
                
                raw = RawContent(
                    id=str(uuid.uuid4()),
                    source_id=source.id,
                    content=item['content'],
                    url=item['url'],
                    timestamp=datetime.now().isoformat(),
                    status=status,
                    analysis_summary=analysis.summary,
                    risk_score=analysis.radicalization_score
                )
                RAW_CONTENT.append(raw)
                new_content_count += 1
                
        except Exception as e:
            print(f"Error processing source {source.name}: {e}")
            
    return {"status": "success", "new_items": new_content_count}

async def fetch_from_source(source: Source) -> List[dict]:
    """
    Fetch data based on source type.
    """
    items = []
    headers = {'User-Agent': 'Mozilla/5.0 (RecaptureBot/1.0)'}
    
    if source.type == 'direct':
        # Simple page scrape
        try:
            res = requests.get(source.url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                # Remove scripts
                for s in soup(["script", "style"]):
                    s.decompose()
                text = soup.get_text(separator=' ', strip=True)
                items.append({
                    "content": text,
                    "url": source.url
                })
        except Exception as e:
            print(f"Fetch error: {e}")
            
    elif source.type == 'rss':
        # Mock RSS logic for now (or use feedparser if installed)
        # For demo, we'll just treat it as a direct link or return a mock item
        items.append({
            "content": f"Mock RSS content from {source.name}. Discussing controversial topics...",
            "url": source.url + "/item1"
        })
        
    return items

from .trend_monitor import add_trend
from .models import DisinformationTrend

async def discover_trends():
    """
    Uses the discovery agent to find broad trending harmful topics and adds them to the database.
    """
    print("Discovering real-time trends...")
    # Broad keywords to find trending harmful content
    discovery_keywords = [
        "latest conspiracy theories 2024",
        "viral misinformation trends",
        "trending harmful social media challenges",
        "popular radicalization narratives"
    ]
    
    discovered = await discover_new_sources(discovery_keywords)
    
    new_trends_count = 0
    for item in discovered:
        # Simple heuristic: If we found it via these keywords, treat it as a potential trend.
        # In a real system, we'd use AI to cluster these into cohesive trends.
        # For MVP, we'll create a trend entry for each distinct high-quality result.
        
        # Check if trend already exists (by topic/title) - simplified check
        # In production, use vector similarity or DB check.
        
        trend = DisinformationTrend(
            id=str(uuid.uuid4()),
            topic=item['title'],
            description=item['snippet'][:200] + "...",
            severity="Medium", # Default, AI could assess this
            common_phrases=[],
            counter_arguments=[],
            sources=[item['url']]
        )
        await add_trend(trend)
        new_trends_count += 1
        
    return {"status": "success", "new_trends": new_trends_count}

async def add_trend_to_queue(trend_id: str):
    """
    Converts a trend into a RawContent item in the pending queue for training.
    """
    from .trend_monitor import get_active_trends
    trends = await get_active_trends()
    trend = next((t for t in trends if t.id == trend_id), None)
    
    if not trend:
        raise ValueError("Trend not found")
        
    # Create RawContent from Trend
    raw = RawContent(
        id=str(uuid.uuid4()),
        source_id="trend_monitor",
        content=f"Trend Topic: {trend.topic}\n\nDescription: {trend.description}\n\nSources: {', '.join(trend.sources)}",
        url=trend.sources[0] if trend.sources else None,
        timestamp=datetime.now().isoformat(),
        status="pending",
        analysis_summary=f"Trend Severity: {trend.severity}",
        risk_score=0.8 if trend.severity == "High" else 0.5
    )
    RAW_CONTENT.append(raw)
    return raw

async def train_approved_batch():
    """
    Trains all approved content in batch and marks them as 'trained'.
    Returns stats about the training operation.
    """
    from .vector_store import add_documents, get_collection_stats
    
    # Get all approved items
    approved_items = [c for c in RAW_CONTENT if c.status == "approved"]
    
    if not approved_items:
        return {"status": "success", "items_trained": 0, "message": "No approved items to train"}
    
    # Prepare batch data
    documents = []
    metadatas = []
    ids = []
    
    for content in approved_items:
        doc_text = f"Threat Intel: {content.content[:500]}... Source: {content.url}"
        documents.append(doc_text)
        metadatas.append({
            "type": "threat_intel",
            "source_id": content.source_id,
            "risk": content.risk_score,
            "url": content.url or "unknown"
        })
        ids.append(f"intel_{content.id}")
    
    # Batch ingest
    add_documents(documents, metadatas, ids)
    
    # Mark as trained
    for content in approved_items:
        content.status = "trained"
    
    # Get updated stats
    stats = get_collection_stats()
    
    return {
        "status": "success",
        "items_trained": len(approved_items),
        "total_documents": stats.get("total_documents", 0),
        "message": f"Successfully trained {len(approved_items)} items"
    }
