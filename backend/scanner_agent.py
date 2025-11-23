from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from .models import ContentLog, AnalysisResponse
from .ai_service import analyze_text
from .rag_service import augment_analysis_with_context
from .profiles import add_content_log
from .database import get_db_connection
import json

router = APIRouter()

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

@router.post("/scanner/ingest", response_model=ContentLog)
async def ingest_content(log: ContentLog, background_tasks: BackgroundTasks):
    """
    Ingest content from a child's device (simulated).
    Triggers background analysis.
    """
    # 1. Save initial log
    saved_log = await add_content_log(log.profile_id, log)
    
    # 2. Trigger background analysis
    background_tasks.add_task(process_content_background, saved_log)
    
    return saved_log
