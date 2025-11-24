import uuid
from datetime import datetime
from typing import List
from .models import Source, RawContent
from .ai_service import analyze_text
from .database import get_db_connection
import requests
from bs4 import BeautifulSoup
import json

async def get_sources() -> List[Source]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources")
    rows = cursor.fetchall()
    conn.close()
    
    sources = []
    for row in rows:
        sources.append(Source(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            type=row['type'],
            status=row['status'],
            last_scraped=row['last_scraped']
        ))
    return sources

async def add_source(source: Source) -> Source:
    if not source.id:
        source.id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sources (id, name, url, type, status, last_scraped) VALUES (?, ?, ?, ?, ?, ?)",
        (source.id, source.name, source.url, source.type, source.status, source.last_scraped)
    )
    conn.commit()
    conn.close()
    return source

async def delete_source(source_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()

async def get_raw_content() -> List[RawContent]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM raw_content ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    content_list = []
    for row in rows:
        content_list.append(RawContent(
            id=row['id'],
            source_id=row['source_id'],
            content=row['content'],
            url=row['url'],
            timestamp=row['timestamp'],
            status=row['status'],
            analysis_summary=row['analysis_summary'],
            risk_score=row['risk_score']
        ))
    return content_list

async def add_raw_content(content: RawContent):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for duplicates by URL if URL exists
    if content.url:
        cursor.execute("SELECT id FROM raw_content WHERE url = ?", (content.url,))
        if cursor.fetchone():
            conn.close()
            return # Skip duplicate
            
    cursor.execute(
        "INSERT INTO raw_content (id, source_id, content, url, timestamp, status, analysis_summary, risk_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (content.id, content.source_id, content.content, content.url, content.timestamp, content.status, content.analysis_summary, content.risk_score)
    )
    conn.commit()
    conn.close()

async def approve_content(content_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE raw_content SET status = 'approved' WHERE id = ?", (content_id,))
    conn.commit()
    conn.close()

async def discard_content(content_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE raw_content SET status = 'discarded' WHERE id = ?", (content_id,))
    conn.commit()
    conn.close()

from .discovery_agent import discover_new_sources

# In-memory topics for demo (could also be moved to DB, but sticking to plan for now)
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
             try:
                # Check duplicates is handled in add_raw_content, but we can check here too if we want to avoid analysis cost
                # For now, let's just process
                
                content_text = item['snippet']
                # Optional: Deep fetch logic here
                
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
                
                await add_raw_content(raw)
                new_content_count += 1
             except Exception as e:
                 print(f"Error processing discovered item {item['url']}: {e}")

    # 1. Fetch from Manual Sources
    sources = await get_sources()
    for source in sources:
        try:
            fetched_items = await fetch_from_source(source)
            
            for item in fetched_items:
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
                
                await add_raw_content(raw)
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
        # Mock RSS logic for now
        items.append({
            "content": f"Mock RSS content from {source.name}. Discussing controversial topics...",
            "url": source.url + "/item1"
        })
        
    return items

from .trend_monitor import add_trend as add_trend_db
from .models import DisinformationTrend

async def discover_trends():
    """
    Uses the discovery agent to find broad trending harmful topics and adds them to the database.
    """
    print("Discovering real-time trends...")
    # Broad keywords to find trending harmful content
    discovery_keywords = [
        "incel ideology manifesto",
        "white supremacy recruitment tactics",
        "pro-ana thinspo communities",
        "violent extremism accelerationism",
        "transphobic hate speech trends",
        "self-harm encouragement groups",
        "radicalization pipeline youtube",
        "neo-nazi propaganda social media"
    ]
    
    discovered = await discover_new_sources(discovery_keywords)
    
    new_trends_count = 0
    for item in discovered:
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
        await add_trend_db(trend)
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
    
    await add_raw_content(raw)
    return raw

async def train_approved_batch():
    """
    Trains all approved content in batch and marks them as 'trained'.
    Returns stats about the training operation.
    """
    from .vector_store import add_documents, get_collection_stats
    
    # Get all approved items from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM raw_content WHERE status = 'approved'")
    rows = cursor.fetchall()
    conn.close()
    
    approved_items = []
    for row in rows:
        approved_items.append(RawContent(
            id=row['id'],
            source_id=row['source_id'],
            content=row['content'],
            url=row['url'],
            timestamp=row['timestamp'],
            status=row['status'],
            analysis_summary=row['analysis_summary'],
            risk_score=row['risk_score']
        ))
    
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
    
    # Mark as trained in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    for content in approved_items:
        cursor.execute("UPDATE raw_content SET status = 'trained' WHERE id = ?", (content.id,))
    conn.commit()
    conn.close()
    
    # Get updated stats
    stats = get_collection_stats()
    
    return {
        "status": "success",
        "items_trained": len(approved_items),
        "total_documents": stats.get("total_documents", 0),
        "message": f"Successfully trained {len(approved_items)} items"
    }
