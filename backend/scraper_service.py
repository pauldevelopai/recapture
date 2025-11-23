from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from .ai_service import analyze_text
from .trend_monitor import add_trend
from .models import DisinformationTrend
import uuid

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str

class ScrapeResponse(BaseModel):
    url: str
    content_preview: str
    analysis: dict

@router.post("/scraper/scan-url", response_model=ScrapeResponse)
async def scan_url(request: ScrapeRequest):
    try:
        # 1. Fetch Content
        # User-Agent to avoid some basic blocking
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
        response = requests.get(request.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 2. Parse Text
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        
        # Truncate for analysis if too long (mock limit)
        text_preview = text[:5000]
        
        # 3. Analyze Content
        analysis_result = await analyze_text(text_preview)
        
        # 4. Auto-Add to Threat DB if Critical (Mock Logic)
        # In a real app, we might want human review first
        if analysis_result.confidence_score > 0.9:
            # Check if we should create a new trend entry or just log it
            # For this demo, we'll just return the analysis
            pass
            
        return ScrapeResponse(
            url=request.url,
            content_preview=text[:200] + "...",
            analysis=analysis_result.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")
