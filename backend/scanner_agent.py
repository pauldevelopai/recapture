from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from pydantic import BaseModel
import uuid
import json

from .models import ContentLog
from .ai_service import analyze_text
from .subjects import add_content_log
from .database import get_db_connection
from .rag_service import augment_analysis_with_context

router = APIRouter()

class IngestRequest(BaseModel):
    profile_id: str # Keeping as profile_id in request for now to match frontend, but mapping to subject_id
    content: str
    source_url: str
    timestamp: str

async def process_content_background(log: ContentLog):
    """
    Background task to analyze content and update the log with results.
    """
    try:
        # 1. Analyze Text
        analysis = await analyze_text(log.content)
        
        # 2. RAG Augmentation
        analysis_dict = analysis.dict()
        analysis_dict = await augment_analysis_with_context(log.content, analysis_dict)
        
        # 3. Update Log in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update the log with the analysis ID and detected trends
        cursor.execute(
            "UPDATE content_logs SET analysis_id = ?, detected_trends = ? WHERE id = ?",
            (
                analysis.id,
                json.dumps(analysis_dict.get("detected_themes", [])),
                log.id
            )
        )
        conn.commit()
        conn.close()
        
        print(f"Processed content log {log.id}: Detected {analysis_dict.get('detected_themes', [])}")
        
    except Exception as e:
        print(f"Error processing content log {log.id}: {e}")

@router.post("/scanner/ingest")
async def ingest_content(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Simulates the scanner agent running on the child's device.
    Receives content, analyzes it, and logs it to the Subject's history.
    """
    try:
        # 1. Analyze Content (Initial quick analysis or just placeholder if doing background)
        # For immediate feedback we might want to do a quick check, but for now let's trust the background process
        # or do a synchronous analysis if needed. The original code did sync analysis.
        # Let's stick to the pattern: Save Log -> Background Process
        
        # Create initial log object
        log = ContentLog(
            id=str(uuid.uuid4()),
            subject_id=request.profile_id,
            content=request.content,
            source_url=request.source_url,
            timestamp=request.timestamp,
            analysis_id=None, # Will be filled by background task
            detected_trends=[]
        )
        
        # Save to DB
        await add_content_log(request.profile_id, log)
        
        # Trigger background analysis
        background_tasks.add_task(process_content_background, log)
        
        return {"status": "ingested", "log_id": log.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
