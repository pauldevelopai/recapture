from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import json
from datetime import datetime
from .models import UserProfile, ContentLog
from .database import get_db_connection

router = APIRouter()

@router.get("/profiles", response_model=List[UserProfile])
async def get_profiles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles")
    rows = cursor.fetchall()
    conn.close()
    
    profiles = []
    for row in rows:
        profiles.append(UserProfile(
            id=row['id'],
            name=row['name'],
            age=row['age'],
            risk_level=row['risk_level'],
            notes=row['notes']
        ))
    return profiles

@router.post("/profiles", response_model=UserProfile)
async def create_profile(profile: UserProfile):
    if not profile.id:
        profile.id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO profiles (id, name, age, risk_level, notes) VALUES (?, ?, ?, ?, ?)",
        (profile.id, profile.name, profile.age, profile.risk_level, profile.notes)
    )
    conn.commit()
    conn.close()
    return profile

@router.get("/profiles/{profile_id}/logs", response_model=List[ContentLog])
async def get_content_logs(profile_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM content_logs WHERE profile_id = ? ORDER BY timestamp DESC", (profile_id,))
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        logs.append(ContentLog(
            id=row['id'],
            profile_id=row['profile_id'],
            content=row['content'],
            source_url=row['source_url'],
            timestamp=row['timestamp'],
            analysis_id=row['analysis_id'],
            detected_trends=json.loads(row['detected_trends']) if row['detected_trends'] else []
        ))
    return logs

@router.post("/profiles/{profile_id}/logs", response_model=ContentLog)
async def add_content_log(profile_id: str, log: ContentLog):
    if not log.id:
        log.id = str(uuid.uuid4())
    
    log.profile_id = profile_id
    if not log.timestamp:
        log.timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO content_logs (id, profile_id, content, source_url, timestamp, analysis_id, detected_trends) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            log.id, 
            log.profile_id, 
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

from .models import Authority

@router.get("/profiles/{profile_id}/authorities", response_model=List[Authority])
async def get_authorities(profile_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM authorities WHERE profile_id = ?", (profile_id,))
    rows = cursor.fetchall()
    conn.close()
    
    authorities = []
    for row in rows:
        authorities.append(Authority(
            id=row['id'],
            profile_id=row['profile_id'],
            name=row['name'],
            role=row['role'],
            relation=row['relation']
        ))
    return authorities

@router.post("/profiles/{profile_id}/authorities", response_model=Authority)
async def add_authority(profile_id: str, authority: Authority):
    if not authority.id:
        authority.id = str(uuid.uuid4())
    authority.profile_id = profile_id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO authorities (id, profile_id, name, role, relation) VALUES (?, ?, ?, ?, ?)",
        (authority.id, authority.profile_id, authority.name, authority.role, authority.relation)
    )
    conn.commit()
    conn.close()
    return authority

@router.delete("/profiles/{profile_id}/authorities/{authority_id}")
async def delete_authority(profile_id: str, authority_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM authorities WHERE id = ? AND profile_id = ?", (authority_id, profile_id))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
