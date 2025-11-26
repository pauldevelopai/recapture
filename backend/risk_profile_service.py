from typing import List, Dict
import json
import uuid
from datetime import datetime
import os
from openai import OpenAI
from .database import get_db_connection
from .models import RiskProfileAnalysis, SubjectSocialPost

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def analyze_post_batch(posts: List[SubjectSocialPost]) -> Dict:
    """
    Analyze a batch of social media posts for risk indicators
    Returns aggregated analysis results
    """
    if not posts:
        return {
            'risk_score': 0.0,
            'themes': [],
            'risk_factors': [],
            'language_patterns': {}
        }
    
    # Prepare posts for analysis
    posts_text = "\n\n".join([
        f"[{post.platform} - {post.posted_at}]: {post.content}"
        for post in posts[:50]  # Limit to 50 most recent posts to stay within token limits
    ])
    
    try:
        # Use OpenAI to analyze the posts
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at analyzing social media content for radicalization risk factors.
Analyze the provided posts and return a JSON object with:
1. risk_score: A score from 0-100 indicating overall radicalization risk
2. themes: List of recurring topics/interests (5-10 items)
3. risk_factors: List of specific concerning elements, each with:
   - factor: Brief description
   - severity: "Low", "Medium", or "High"
   - evidence: Quote or example from posts
4. language_patterns: Object with:
   - tone: Overall emotional tone (e.g., "angry", "isolated", "hopeful")
   - vocabulary_level: Assessment of language sophistication
   - sentiment_trend: How sentiment changes over time

Focus on indicators like:
- Isolation and alienation
- Violent rhetoric or imagery
- Conspiracy theories
- Dehumanization of groups
- Glorification of extremist figures
- Sudden changes in behavior or language"""
                },
                {
                    "role": "user",
                    "content": f"Analyze these social media posts:\n\n{posts_text}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error in analyze_post_batch: {e}")
        return {
            'risk_score': 0.0,
            'themes': [],
            'risk_factors': [],
            'language_patterns': {},
            'error': str(e)
        }


async def extract_themes(posts: List[SubjectSocialPost]) -> List[str]:
    """Extract recurring themes and interests from posts"""
    if not posts:
        return []
    
    posts_text = " ".join([post.content for post in posts[:30]])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Extract 5-10 main themes, topics, or interests from these social media posts. Return as a JSON array of strings."
                },
                {
                    "role": "user",
                    "content": posts_text
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('themes', [])
        
    except Exception as e:
        print(f"Error extracting themes: {e}")
        return []


async def detect_radicalization_markers(posts: List[SubjectSocialPost]) -> List[Dict]:
    """Look for specific radicalization warning signs"""
    if not posts:
        return []
    
    posts_text = "\n".join([f"{post.platform}: {post.content}" for post in posts[:40]])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Identify specific radicalization markers in these posts.
Look for:
- Violent rhetoric or threats
- Conspiracy theories
- "Us vs. Them" mentality
- Dehumanization
- Glorification of violence or extremist figures
- Calls to action for harmful behavior

Return a JSON array of markers found, each with:
- type: Category of marker
- severity: "Low", "Medium", or "High"
- evidence: Quote from the post
- post_index: Which post number contained this"""
                },
                {
                    "role": "user",
                    "content": posts_text
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('markers', [])
        
    except Exception as e:
        print(f"Error detecting radicalization markers: {e}")
        return []


async def analyze_language_patterns(posts: List[SubjectSocialPost]) -> Dict:
    """Analyze writing style and language patterns for changes over time"""
    if not posts:
        return {}
    
    # Group posts by time period for trend analysis
    posts_text = "\n".join([
        f"[{post.posted_at or 'unknown'}]: {post.content}"
        for post in sorted(posts[:30], key=lambda p: p.posted_at or "")
    ])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Analyze the language patterns in these chronologically ordered posts.
Return a JSON object with:
- tone: Overall emotional tone
- vocabulary_level: Assessment of language sophistication
- sentiment_trend: How sentiment changes from earliest to latest posts
- red_flags: Any concerning language shifts (e.g., increased aggression, isolation)"""
                },
                {
                    "role": "user",
                    "content": posts_text
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error analyzing language patterns: {e}")
        return {}


async def build_risk_profile(subject_id: str) -> RiskProfileAnalysis:
    """
    Build comprehensive risk profile for a subject based on their social media posts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all posts for this subject
    cursor.execute(
        """SELECT * FROM subject_social_posts 
        WHERE subject_id = ? 
        ORDER BY posted_at DESC""",
        (subject_id,)
    )
    
    post_rows = cursor.fetchall()
    
    if not post_rows:
        # No posts to analyze
        profile = RiskProfileAnalysis(
            id=str(uuid.uuid4()),
            subject_id=subject_id,
            analysis_date=datetime.now().isoformat(),
            overall_risk_score=0.0,
            risk_factors=[],
            detected_themes=[],
            language_patterns={},
            post_count=0
        )
    else:
        # Convert to SubjectSocialPost objects
        posts = []
        for row in post_rows:
            posts.append(SubjectSocialPost(
                id=row['id'],
                subject_id=row['subject_id'],
                feed_id=row['feed_id'],
                content=row['content'],
                posted_at=row['posted_at'],
                platform=row['platform'],
                url=row['url'],
                engagement_metrics=json.loads(row['engagement_metrics']) if row['engagement_metrics'] else None,
                scraped_at=row['scraped_at']
            ))
        
        # Perform analysis
        batch_analysis = await analyze_post_batch(posts)
        themes = await extract_themes(posts)
        markers = await detect_radicalization_markers(posts)
        language = await analyze_language_patterns(posts)
        
        # Combine marker-based risk factors with batch analysis
        all_risk_factors = batch_analysis.get('risk_factors', [])
        for marker in markers:
            all_risk_factors.append({
                'factor': marker.get('type', 'Unknown'),
                'severity': marker.get('severity', 'Medium'),
                'evidence': marker.get('evidence', '')
            })
        
        profile = RiskProfileAnalysis(
            id=str(uuid.uuid4()),
            subject_id=subject_id,
            analysis_date=datetime.now().isoformat(),
            overall_risk_score=batch_analysis.get('risk_score', 0.0),
            risk_factors=all_risk_factors,
            detected_themes=themes or batch_analysis.get('themes', []),
            language_patterns=language or batch_analysis.get('language_patterns', {}),
            post_count=len(posts)
        )
    
    # Save to database
    cursor.execute(
        """INSERT INTO risk_profile_analyses 
        (id, subject_id, analysis_date, overall_risk_score, risk_factors, detected_themes, language_patterns, post_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            profile.id,
            profile.subject_id,
            profile.analysis_date,
            profile.overall_risk_score,
            json.dumps(profile.risk_factors),
            json.dumps(profile.detected_themes),
            json.dumps(profile.language_patterns),
            profile.post_count
        )
    )
    
    conn.commit()
    conn.close()
    
    return profile


async def get_latest_risk_profile(subject_id: str) -> RiskProfileAnalysis:
    """Get the most recent risk profile for a subject"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM risk_profile_analyses 
        WHERE subject_id = ? 
        ORDER BY analysis_date DESC 
        LIMIT 1""",
        (subject_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return RiskProfileAnalysis(
        id=row['id'],
        subject_id=row['subject_id'],
        analysis_date=row['analysis_date'],
        overall_risk_score=row['overall_risk_score'],
        risk_factors=json.loads(row['risk_factors']) if row['risk_factors'] else [],
        detected_themes=json.loads(row['detected_themes']) if row['detected_themes'] else [],
        language_patterns=json.loads(row['language_patterns']) if row['language_patterns'] else {},
        post_count=row['post_count']
    )


async def update_risk_profile(subject_id: str) -> RiskProfileAnalysis:
    """
    Update risk profile with new posts (incremental update)
    """
    # For now, we'll just rebuild the entire profile
    # In the future, this could be optimized to only analyze new posts
    return await build_risk_profile(subject_id)
