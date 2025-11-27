"""
Risk Monitoring Service
Detects when subjects need intervention based on content patterns and risk escalation.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .database import get_db_connection
import json

class RiskMonitor:
    
    # Escalation thresholds
    VIOLENCE_KEYWORDS = [
        "hate them", "kill", "weapon", "gun", "knife", "attack", "revenge",
        "burn it down", "destroy", "violence", "hurt"
    ]
    
    ISOLATION_KEYWORDS = [
        "alone", "lonely", "rotting", "ldar", "no friends", "no one cares",
        "forgotten", "invisible", "isolation"
    ]
    
    HOPELESSNESS_KEYWORDS = [
        "it's over", "no hope", "give up", "pointless", "why try", 
        "doomed", "blackpill", "cope", "rope"
    ]
    
    @staticmethod
    def analyze_subject_risk(subject_id: str) -> Dict:
        """
        Analyze a subject's risk level and return escalation indicators.
        
        Returns:
            {
                "subject_id": str,
                "current_risk_score": float (0-10),
                "risk_trend": str ("stable", "increasing", "decreasing"),
                "escalation_indicators": List[str],
                "needs_intervention": bool,
                "confidence": float (0-1)
            }
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subject's current risk level
        cursor.execute("SELECT risk_level FROM subjects WHERE id = ?", (subject_id,))
        subject_row = cursor.fetchone()
        if not subject_row:
            conn.close()
            return None
            
        current_risk_level = subject_row['risk_level']
        risk_score_map = {"Low": 2, "Medium": 5, "High": 8, "Critical": 10}
        current_score = risk_score_map.get(current_risk_level, 5)
        
        # Get recent posts (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute(
            """SELECT content, posted_at FROM subject_social_posts 
            WHERE subject_id = ? AND posted_at > ?
            ORDER BY posted_at DESC""",
            (subject_id, seven_days_ago)
        )
        recent_posts = cursor.fetchall()
        
        # Get older posts for comparison (7-30 days ago)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute(
            """SELECT content FROM subject_social_posts 
            WHERE subject_id = ? AND posted_at BETWEEN ? AND ?""",
            (subject_id, thirty_days_ago, seven_days_ago)
        )
        older_posts = cursor.fetchall()
        
        conn.close()
        
        # Analysis
        escalation_indicators = []
        
        # 1. Check post frequency
        recent_count = len(recent_posts)
        older_count = len(older_posts)
        
        if recent_count > older_count * 1.5 and recent_count > 5:
            escalation_indicators.append(f"Increased posting frequency ({recent_count} posts in 7 days vs {older_count} in previous 23 days)")
        
        # 2. Analyze content themes
        violence_count = 0
        isolation_count = 0
        hopelessness_count = 0
        
        all_recent_text = " ".join([p['content'].lower() for p in recent_posts])
        
        for keyword in RiskMonitor.VIOLENCE_KEYWORDS:
            if keyword in all_recent_text:
                violence_count += all_recent_text.count(keyword)
        
        for keyword in RiskMonitor.ISOLATION_KEYWORDS:
            if keyword in all_recent_text:
                isolation_count += all_recent_text.count(keyword)
                
        for keyword in RiskMonitor.HOPELESSNESS_KEYWORDS:
            if keyword in all_recent_text:
                hopelessness_count += all_recent_text.count(keyword)
        
        if violence_count > 2:
            escalation_indicators.append(f"Violence-related language detected ({violence_count} instances)")
            current_score += 2
            
        if isolation_count > 3:
            escalation_indicators.append(f"Social isolation indicators ({isolation_count} instances)")
            current_score += 1
            
        if hopelessness_count > 4:
            escalation_indicators.append(f"Hopelessness/despair language ({hopelessness_count} instances)")
            current_score += 1.5
        
        # 3. Check for sudden spike in harmful content
        if recent_count >= 5:
            harmful_post_ratio = (violence_count + isolation_count + hopelessness_count) / recent_count
            if harmful_post_ratio > 0.6:
                escalation_indicators.append("High concentration of concerning content")
                current_score += 1
        
        # Cap score at 10
        current_score = min(current_score, 10)
        
        # Determine trend
        if current_score > risk_score_map.get(current_risk_level, 5) + 1:
            trend = "increasing"
        elif current_score < risk_score_map.get(current_risk_level, 5) - 1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Determine if intervention needed
        needs_intervention = (
            current_score >= 7 or 
            len(escalation_indicators) >= 3 or
            violence_count >= 3
        )
        
        # Calculate confidence (based on data availability)
        confidence = min(1.0, (recent_count + older_count) / 20)
        
        return {
            "subject_id": subject_id,
            "current_risk_score": round(current_score, 1),
            "risk_trend": trend,
            "escalation_indicators": escalation_indicators,
            "needs_intervention": needs_intervention,
            "confidence": round(confidence, 2),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def get_at_risk_subjects() -> List[Dict]:
        """
        Get all subjects who currently need intervention.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, risk_level FROM subjects")
        subjects = cursor.fetchall()
        conn.close()
        
        at_risk = []
        for subject in subjects:
            analysis = RiskMonitor.analyze_subject_risk(subject['id'])
            if analysis and analysis['needs_intervention']:
                at_risk.append({
                    "id": subject['id'],
                    "name": subject['name'],
                    "current_risk_level": subject['risk_level'],
                    "analysis": analysis
                })
        
        # Sort by risk score descending
        at_risk.sort(key=lambda x: x['analysis']['current_risk_score'], reverse=True)
        
        return at_risk
