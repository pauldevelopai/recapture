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

class UserProfile(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    risk_level: str = "Low" # Low, Medium, High
    notes: Optional[str] = None

class ContentLog(BaseModel):
    id: Optional[str] = None
    profile_id: str
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
    profile_id: str
    name: str
    role: str
    relation: str
