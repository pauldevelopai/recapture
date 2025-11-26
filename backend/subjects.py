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

# Social Media Feed Endpoints
from .models import SocialMediaFeed, SubjectSocialPost, RiskProfileAnalysis
from .social_media_service import scrape_subject_feeds, get_subject_posts
from .risk_profile_service import build_risk_profile, get_latest_risk_profile

@router.get("/subjects/{subject_id}/social-feeds", response_model=List[SocialMediaFeed])
async def get_social_feeds(subject_id: str):
    """Get all social media feeds for a subject"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_media_feeds WHERE subject_id = ?", (subject_id,))
    rows = cursor.fetchall()
    conn.close()
    
    feeds = []
    for row in rows:
        feeds.append(SocialMediaFeed(
            id=row['id'],
            subject_id=row['subject_id'],
            platform=row['platform'],
            username=row['username'],
            profile_url=row['profile_url'],
            status=row['status'],
            last_scraped=row['last_scraped'],
            error_message=row['error_message']
        ))
    return feeds

@router.post("/subjects/{subject_id}/social-feeds", response_model=SocialMediaFeed)
async def add_social_feed(subject_id: str, feed: SocialMediaFeed):
    """Add a new social media feed for a subject"""
   # Set subject_id from path parameter, not from body
    feed.subject_id = subject_id
    
    # Generate ID if not provided
    if not feed.id:
        feed.id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO social_media_feeds 
        (id, subject_id, platform, username, profile_url, status, last_scraped, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (feed.id, feed.subject_id, feed.platform, feed.username, feed.profile_url, 
         feed.status or 'active', feed.last_scraped, feed.error_message)
    )
    conn.commit()
    conn.close()
    return feed

@router.delete("/subjects/{subject_id}/social-feeds/{feed_id}")
async def delete_social_feed(subject_id: str, feed_id: str):
    """Delete a social media feed"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM social_media_feeds WHERE id = ? AND subject_id = ?", (feed_id, subject_id))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@router.post("/subjects/{subject_id}/scrape-feeds")
async def scrape_feeds(subject_id: str):
    """Manually trigger scraping of all social media feeds for a subject"""
    result = await scrape_subject_feeds(subject_id)
    return result

@router.get("/subjects/{subject_id}/social-posts", response_model=List[SubjectSocialPost])
async def get_social_posts(subject_id: str, limit: int = 100, offset: int = 0):
    """Get social media posts for a subject"""
    posts = await get_subject_posts(subject_id, limit, offset)
    return posts

@router.get("/subjects/{subject_id}/risk-profile", response_model=RiskProfileAnalysis)
async def get_risk_profile(subject_id: str):
    """Get the latest risk profile for a subject"""
    profile = await get_latest_risk_profile(subject_id)
    if not profile:
        # No profile exists, build one
        profile = await build_risk_profile(subject_id)
    return profile

@router.post("/subjects/{subject_id}/risk-profile", response_model=RiskProfileAnalysis)
async def update_risk_profile_endpoint(subject_id: str):
    """Rebuild risk profile based on current social media posts"""
    profile = await build_risk_profile(subject_id)
    return profile
