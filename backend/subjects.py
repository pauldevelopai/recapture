from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import json
from datetime import datetime
from .models import Subject, ContentLog, Authority
from .database import get_db_connection

router = APIRouter()

@router.get("/subjects", response_model=List[Subject])
async def get_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    rows = cursor.fetchall()
    conn.close()
    
    subjects = []
    for row in rows:
        subjects.append(Subject(
            id=row['id'],
            name=row['name'],
            age=row['age'],
            risk_level=row['risk_level'],
            notes=row['notes']
        ))
    return subjects

@router.post("/subjects", response_model=Subject)
async def create_subject(subject: Subject):
    if not subject.id:
        subject.id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (id, name, age, risk_level, notes) VALUES (?, ?, ?, ?, ?)",
        (subject.id, subject.name, subject.age, subject.risk_level, subject.notes)
    )
    conn.commit()
    conn.close()
    return subject

@router.get("/subjects/{subject_id}/logs", response_model=List[ContentLog])
async def get_content_logs(subject_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM content_logs WHERE subject_id = ? ORDER BY timestamp DESC", (subject_id,))
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        logs.append(ContentLog(
            id=row['id'],
            subject_id=row['subject_id'],
            content=row['content'],
            source_url=row['source_url'],
            timestamp=row['timestamp'],
            analysis_id=row['analysis_id'],
            detected_trends=json.loads(row['detected_trends']) if row['detected_trends'] else []
        ))
    return logs

@router.post("/subjects/{subject_id}/logs", response_model=ContentLog)
async def add_content_log(subject_id: str, log: ContentLog):
    if not log.id:
        log.id = str(uuid.uuid4())
    
    log.subject_id = subject_id
    if not log.timestamp:
        log.timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO content_logs (id, subject_id, content, source_url, timestamp, analysis_id, detected_trends) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            log.id, 
            log.subject_id, 
            log.content, 
            log.source_url, 
            log.timestamp, 
            log.analysis_id,
            json.dumps(log.detected_trends)
        )
    )
    conn.commit()
    conn.close()
    return log

@router.get("/subjects/{subject_id}/authorities", response_model=List[Authority])
async def get_authorities(subject_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM authorities WHERE subject_id = ?", (subject_id,))
    rows = cursor.fetchall()
    conn.close()
    
    authorities = []
    for row in rows:
        authorities.append(Authority(
            id=row['id'],
            subject_id=row['subject_id'],
            name=row['name'],
            role=row['role'],
            relation=row['relation']
        ))
    return authorities

@router.post("/subjects/{subject_id}/authorities", response_model=Authority)
async def add_authority(subject_id: str, authority: Authority):
    if not authority.id:
        authority.id = str(uuid.uuid4())
    authority.subject_id = subject_id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO authorities (id, subject_id, name, role, relation) VALUES (?, ?, ?, ?, ?)",
        (authority.id, authority.subject_id, authority.name, authority.role, authority.relation)
    )
    conn.commit()
    conn.close()
    return authority

@router.delete("/subjects/{subject_id}/authorities/{authority_id}")
async def delete_authority(subject_id: str, authority_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM authorities WHERE id = ? AND subject_id = ?", (authority_id, subject_id))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
