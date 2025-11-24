from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .models import AnalysisRequest, AnalysisResponse, ArgumentRequest, ArgumentResponse, DisinformationTrend
from .ai_service import analyze_text, generate_argument
from .trend_monitor import get_active_trends, add_trend
from .rag_service import augment_analysis_with_context, chat_with_data, retrieve_context
from .database import init_db, get_db_connection
from .subjects import router as subjects_router
from .scanner_agent import router as scanner_router
from .scraper_service import router as scraper_router_service
from .ingest_service import ingest_all_data
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    # Ingest data into Vector DB on startup
    await ingest_all_data()
    yield
    # Shutdown

app = FastAPI(title="RECAPTURE API", description="API for reversing radicalization in young people", lifespan=lifespan)

app.include_router(subjects_router, prefix="/api")
app.include_router(scanner_router, prefix="/api")
app.include_router(scraper_router_service, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to RECAPTURE API"}

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = await chat_with_data(request.query)
    return {"response": response}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    try:
        # 1. Basic Analysis
        result = await analyze_text(request.text)
        
        # 2. Augment with RAG (Knowledge Base)
        result_dict = result.dict()
        result_dict = await augment_analysis_with_context(request.text, result_dict)
        
        # 3. Log to Subject if provided
        if request.profile_id: # Keeping request field name for now, but treating as subject_id
            from .models import ContentLog
            from .subjects import add_content_log
            import uuid
            from datetime import datetime
            
            log = ContentLog(
                id=str(uuid.uuid4()),
                subject_id=request.profile_id,
                content=request.text,
                source_url=request.source_url,
                timestamp=datetime.now().isoformat(),
                analysis_id=result.id,
                detected_trends=result_dict.get("detected_themes", [])
            )
            await add_content_log(request.profile_id, log)
        
        return AnalysisResponse(**result_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends", response_model=List[DisinformationTrend])
async def get_trends():
    return await get_active_trends()

@app.post("/trends", response_model=DisinformationTrend)
async def create_trend(trend: DisinformationTrend):
    return await add_trend(trend)

from .pipeline_service import discover_trends

@app.post("/trends/refresh")
async def refresh_trends():
    return await discover_trends()


from .pipeline_service import add_trend_to_queue

@app.post("/trends/{trend_id}/queue")
async def queue_trend(trend_id: str):
    try:
        await add_trend_to_queue(trend_id)
        return {"status": "queued"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

class ArgumentRequest(BaseModel):
    analysis_id: Optional[str] = None
    context: Optional[str] = None
    profile_id: Optional[str] = None # Treating as subject_id

@app.post("/api/generate-argument", response_model=ArgumentResponse)
async def create_argument(request: ArgumentRequest):
    try:
        # 1. Fetch Subject Data
        subject_data = None
        history_data = []
        authorities_data = []
        
        if request.profile_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Fetch Subject
            cursor.execute("SELECT * FROM subjects WHERE id = ?", (request.profile_id,))
            row = cursor.fetchone()
            if row:
                subject_data = {
                    "name": row['name'],
                    "age": row['age'],
                    "risk_level": row['risk_level'],
                    "notes": row['notes']
                }
            
            # Fetch Recent History
            cursor.execute("SELECT * FROM content_logs WHERE subject_id = ? ORDER BY timestamp DESC LIMIT 5", (request.profile_id,))
            log_rows = cursor.fetchall()
            for log in log_rows:
                history_data.append({
                    "content": log['content'],
                    "timestamp": log['timestamp']
                })
                
            # Fetch Authorities
            cursor.execute("SELECT * FROM authorities WHERE subject_id = ?", (request.profile_id,))
            auth_rows = cursor.fetchall()
            for auth in auth_rows:
                authorities_data.append({
                    "name": auth['name'],
                    "role": auth['role'],
                    "relation": auth['relation']
                })
            
            conn.close()

        # 2. Fetch RAG Context
        rag_context = await retrieve_context(request.context or "")

        # 3. Generate Argument
        result = await generate_argument(
            topic=request.context,
            profile=subject_data, # Passing subject data as 'profile' to keep AI service compatible for now
            history=history_data,
            authorities=authorities_data,
            rag_context=rag_context
        )
        return result
    except Exception as e:
        print(f"Error in generate-argument: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    # Placeholder for database retrieval
    return {"history": []}

# --- Threat Intelligence Pipeline Endpoints ---
from .pipeline_service import get_sources, add_source, delete_source, get_raw_content, approve_content, discard_content, run_pipeline
from .models import Source, RawContent

@app.get("/sources", response_model=List[Source])
async def list_sources():
    return await get_sources()

@app.post("/sources", response_model=Source)
async def create_source(source: Source):
    return await add_source(source)

@app.delete("/sources/{source_id}")
async def remove_source(source_id: str):
    await delete_source(source_id)
    return {"status": "deleted"}

@app.get("/pipeline/content", response_model=List[RawContent])
async def list_pipeline_content():
    return await get_raw_content()

@app.post("/pipeline/run")
async def trigger_pipeline():
    return await run_pipeline()

@app.post("/pipeline/content/{content_id}/approve")
async def approve_pipeline_content(content_id: str):
    await approve_content(content_id)
    return {"status": "approved"}

@app.post("/pipeline/content/{content_id}/discard")
async def discard_pipeline_content(content_id: str):
    await discard_content(content_id)
    return {"status": "discarded"}

from .pipeline_service import train_approved_batch

@app.post("/pipeline/train-batch")
async def train_batch():
    result = await train_approved_batch()
    return result

from .vector_store import get_collection_stats

@app.get("/pipeline/stats")
async def get_pipeline_stats():
    return get_collection_stats()

from .pipeline_service import add_topic, get_topics

@app.get("/topics", response_model=List[str])
async def list_topics():
    return await get_topics()

@app.post("/topics")
async def create_topic(topic: str):
    await add_topic(topic)
    return {"status": "added"}

# --- Deep Listening Endpoints ---
from .listening_service import listening_service
from .models import ListeningResult

@app.post("/api/listening/start")
async def start_listening():
    await listening_service.start_listening()
    return {"status": "started"}

@app.post("/api/listening/stop")
async def stop_listening():
    await listening_service.stop_listening()
    return {"status": "stopped"}

@app.get("/api/listening/status")
async def get_listening_status():
    return {"running": listening_service.is_running()}

@app.get("/api/listening/feed", response_model=List[ListeningResult])
async def get_listening_feed():
    return listening_service.get_latest_results()

@app.post("/api/listening/promote")
async def promote_listening_result(result: ListeningResult):
    """
    Promotes a listening result to the main pipeline for training.
    """
    from .pipeline_service import add_raw_content
    from .models import RawContent
    import uuid
    from datetime import datetime
    
    # Create RawContent from ListeningResult
    content = RawContent(
        id=str(uuid.uuid4()),
        source_id="listening_service", # specific source ID for promoted content
        content=f"[{result.source_platform}] {result.content}",
        url=result.url,
        timestamp=datetime.now().isoformat(),
        status="pending",
        risk_score=0.8 if result.severity in ["High", "Critical"] else 0.5,
        analysis_summary=f"Promoted from Listening Feed. Matched Trend: {result.matched_trend_topic}"
    )
    
    await add_raw_content(content)
    return {"status": "promoted", "id": content.id}
