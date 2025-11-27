from pydantic import BaseModel
from typing import List, Optional

class AnalysisRequest(BaseModel):
    text: str
    source_url: Optional[str] = None
    profile_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: str
    radicalization_score: float
    detected_themes: List[str]
    summary: str

class ArgumentRequest(BaseModel):
    analysis_id: str
    context: Optional[str] = None

class ArgumentResponse(BaseModel):
    argument_text: str
    talking_points: List[str]

class DisinformationTrend(BaseModel):
    id: str
    topic: str
    description: str
    severity: str  # e.g., "High", "Medium", "Low"
    common_phrases: List[str]
    counter_arguments: List[str]
    sources: List[str] = [] # e.g. ["YouTube", "TikTok", "4chan"]

class RedFlag(BaseModel):
    id: str
    phrase: str
    category: str
    associated_trend_id: Optional[str] = None

class Subject(BaseModel):
    id: str
    name: str
    age: int
    risk_level: str  # e.g., "Low", "Medium", "High", "Critical"
    notes: Optional[str] = None

class ContentLog(BaseModel):
    id: Optional[str] = None
    subject_id: str
    content: str
    source_url: Optional[str] = None
    timestamp: Optional[str] = None # ISO format
    analysis_id: Optional[str] = None
    detected_trends: List[str] = []

class Source(BaseModel):
    id: Optional[str] = None
    name: str
    url: str
    type: str = "direct" # direct, rss, social
    status: str = "active" # active, inactive
    last_scraped: Optional[str] = None

class RawContent(BaseModel):
    id: Optional[str] = None
    source_id: str
    content: str
    url: Optional[str] = None
    timestamp: Optional[str] = None
    status: str = "pending" # pending, approved, discarded
    analysis_summary: Optional[str] = None
    risk_score: float = 0.0

class Authority(BaseModel):
    id: Optional[str] = None
    subject_id: Optional[str] = None # Optional because it can be inferred from URL
    name: str
    role: str
    relation: str

class ListeningResult(BaseModel):
    id: str
    source_platform: str  # e.g., "Twitter", "4chan"
    author: str
    content: str
    timestamp: str
    matched_trend_id: Optional[str] = None
    matched_trend_topic: Optional[str] = None
    severity: str = "Low"
    url: Optional[str] = None

# Social Media Integration Models
class SocialMediaFeed(BaseModel):
    id: Optional[str] = None
    subject_id: Optional[str] = None  # Set from URL path
    platform: str  # e.g., "Twitter", "Instagram", "TikTok", "Facebook"
    username: Optional[str] = None
    profile_url: Optional[str] = None
    status: Optional[str] = "active"  # "active", "error", "inactive"
    last_scraped: Optional[str] = None
    error_message: Optional[str] = None

class SubjectSocialPost(BaseModel):
    id: Optional[str] = None
    subject_id: str
    feed_id: str
    content: str
    posted_at: Optional[str] = None
    platform: str
    url: Optional[str] = None
    engagement_metrics: Optional[dict] = None  # likes, shares, comments
    scraped_at: Optional[str] = None

class RiskProfileAnalysis(BaseModel):
    id: Optional[str] = None
    subject_id: str
    analysis_date: str
    overall_risk_score: float = 0.0
    risk_factors: List[dict] = []  # [{"factor": "...", "severity": "...", "evidence": "..."}]
    detected_themes: List[str] = []
    language_patterns: dict = {}  # {"tone": "...", "vocabulary_level": "...", "sentiment_trend": "..."}
    post_count: int = 0

# Digital Clone Models
class DigitalClone(BaseModel):
    id: Optional[str] = None
    subject_id: str
    personality_model: dict = {}  # {"traits": [...], "values": [...], "communication_style": "..."}
    writing_style: dict = {}  # {"vocabulary": [...], "sentence_structure": "...", "tone": "..."}
    interests: List[str] = []
    beliefs: dict = {}  # {"topic": "belief/opinion"}
    last_trained: Optional[str] = None
    training_post_count: int = 0
    status: str = "untrained"  # untrained, training, ready, error

class CloneMessage(BaseModel):
    role: str  # "user" or "clone"
    content: str
    timestamp: str

class CloneConversation(BaseModel):
    id: Optional[str] = None
    clone_id: str
    conversation: List[CloneMessage] = []
    effectiveness_score: Optional[float] = None
    timestamp: str
    notes: Optional[str] = None

class CloneTestRequest(BaseModel):
    clone_id: str
    message: str

class CloneTestResponse(BaseModel):
    clone_response: str
    effectiveness_score: float
    suggestions: List[str] = []
    conversation_id: str

# Bot Farm & Campaign Models
class BotFarm(BaseModel):
    id: str
    name: str
    origin_country: str
    network_size: int # Number of bots
    active_campaigns: List[str] = []
    status: str = "Active" # Active, Dormant, Suspended
    primary_tactics: List[str] = [] # e.g., "Hashtag Flooding", "Reply Guy", "Fake News"

class DisinformationCampaign(BaseModel):
    id: str
    name: str
    target_demographic: str
    narrative_goal: str
    active_platforms: List[str]
    bot_farm_id: Optional[str] = None
    reach_estimate: int
    status: str = "Active"
    detected_at: str

