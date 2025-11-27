from fastapi import APIRouter, HTTPException
from typing import List, Optional
from .models import DigitalClone, CloneTestRequest, CloneTestResponse, CloneConversation
from .digital_clone_service import (
    get_or_create_clone,
    train_clone,
    chat_with_clone,
    get_or_create_clone,
    train_clone,
    chat_with_clone,
    get_clone_conversations,
    get_all_clones
)

router = APIRouter()


@router.get("/clones", response_model=List[DigitalClone])
async def list_clones():
    """Get all digital clones"""
    try:
        return await get_all_clones()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clones/{subject_id}", response_model=DigitalClone)
async def get_clone(subject_id: str):
    """Get or create a digital clone for a subject"""
    try:
        clone = await get_or_create_clone(subject_id)
        return clone
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clones/{clone_id}/train", response_model=DigitalClone)
async def retrain_clone(clone_id: str):
    """Retrain a digital clone with latest social media data"""
    from .database import get_db_connection
    
    # Get subject_id from clone_id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subject_id FROM digital_clones WHERE id = ?", (clone_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Clone not found")
    
    try:
        clone = await train_clone(row['subject_id'])
        return clone
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clones/{clone_id}/chat", response_model=CloneTestResponse)
async def send_message_to_clone(clone_id: str, request: CloneTestRequest):
    """Send a message to the clone and get a response with effectiveness evaluation"""
    try:
        result = await chat_with_clone(clone_id, request.message)
        return CloneTestResponse(
            clone_response=result['clone_response'],
            effectiveness_score=result['effectiveness_score'],
            suggestions=result['suggestions'],
            conversation_id=result['conversation_id']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clones/{clone_id}/conversations", response_model=List[CloneConversation])
async def get_conversations(clone_id: str):
    """Get all conversation history for a clone"""
    try:
        conversations = await get_clone_conversations(clone_id)
        return conversations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clones/{clone_id}/conversations/{conversation_id}")
async def delete_conversation(clone_id: str, conversation_id: str):
    """Delete a specific conversation"""
    from .database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM clone_conversations WHERE id = ? AND clone_id = ?",
        (conversation_id, clone_id)
    )
    conn.commit()
    conn.close()
    return {"status": "deleted"}
