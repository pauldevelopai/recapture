"""
Authority Matching Service
Matches subjects with appropriate authorities based on risk factors and specializations.
"""
from typing import List, Dict, Optional
from .database import get_db_connection
import json

class AuthorityMatcher:
    
    # Authority specialization taxonomy
    AUTHORITY_TYPES = {
        "Mental Health Professional": {
            "handles": ["incel", "depression", "isolation", "self-harm", "blackpill", "hopelessness"],
            "effectiveness": 0.9
        },
        "Religious Leader": {
            "handles": ["nihilism", "purpose", "meaning", "morality"],
            "effectiveness": 0.7
        },
        "Parent": {
            "handles": ["general", "support", "boundaries", "early-stage"],
            "effectiveness": 0.8
        },
        "Teacher": {
            "handles": ["conspiracy", "misinformation", "critical-thinking", "education"],
            "effectiveness": 0.6
        },
        "Law Enforcement": {
            "handles": ["violence", "extremism", "accelerationism", "threats", "weapons"],
            "effectiveness": 0.85
        },
        "Peer Counselor": {
            "handles": ["loneliness", "social-anxiety", "relatability", "connection"],
            "effectiveness": 0.65
        },
        "Coach": {
            "handles": ["motivation", "discipline", "self-improvement", "masculinity"],
            "effectiveness": 0.7
        }
    }
    
    @staticmethod
    def extract_themes_from_posts(subject_id: str) -> List[str]:
        """Extract primary themes from subject's social media posts."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT content FROM subject_social_posts 
            WHERE subject_id = ? 
            ORDER BY posted_at DESC LIMIT 20""",
            (subject_id,)
        )
        posts = cursor.fetchall()
        conn.close()
        
        if not posts:
            return ["general"]
        
        all_content = " ".join([p['content'].lower() for p in posts])
        
        themes = []
        
        # Incel/Blackpill indicators
        if any(word in all_content for word in ["blackpill", "chad", "stacy", "incel", "cope", "rope"]):
            themes.append("incel")
            
        # Accelerationism/Extremism
        if any(word in all_content for word in ["accelerat", "collapse", "burn it down", "system", "revolution"]):
            themes.append("accelerationism")
            themes.append("extremism")
            
        # Violence
        if any(word in all_content for word in ["weapon", "gun", "kill", "attack", "violence", "hurt", "hate them"]):
            themes.append("violence")
            themes.append("threats")
            
        # Isolation/Loneliness
        if any(word in all_content for word in ["alone", "lonely", "no friends", "isolation", "rotting"]):
            themes.append("isolation")
            themes.append("loneliness")
            
        # Hopelessness/Depression
        if any(word in all_content for word in ["no hope", "pointless", "why try", "give up", "it's over"]):
            themes.append("hopelessness")
            themes.append("depression")
            
        # Nihilism
        if any(word in all_content for word in ["meaningless", "pointless", "nothing matters", "nihil"]):
            themes.append("nihilism")
            
        if not themes:
            themes.append("general")
            
        return list(set(themes))  # Remove duplicates
    
    @staticmethod
    def score_authority_match(authority: Dict, themes: List[str], relationship_strength: float = 0.5) -> Dict:
        """
        Score how well an authority matches the subject's needs.
        
        Returns:
            {
                "authority": authority_dict,
                "match_score": float (0-1),
                "matching_themes": List[str],
                "confidence": float (0-1)
            }
        """
        authority_role = authority.get('role', '')
        
        # Find authority type config
        authority_config = AuthorityMatcher.AUTHORITY_TYPES.get(authority_role, {
            "handles": [],
            "effectiveness": 0.5
        })
        
        # Calculate theme match
        matching_themes = []
        for theme in themes:
            if theme in authority_config.get("handles", []):
                matching_themes.append(theme)
        
        if not themes:
            theme_match_score = 0.5
        else:
            theme_match_score = len(matching_themes) / len(themes)
        
        # Calculate overall score
        # Formula: theme_match (40%) + relationship (30%) + effectiveness (20%) + availability (10%)
        effectiveness = authority_config.get("effectiveness", 0.5)
        availability = 1.0  # Default, could be dynamic if we track authority status
        
        match_score = (
            theme_match_score * 0.4 +
            relationship_strength * 0.3 +
            effectiveness * 0.2 +
            availability * 0.1
        )
        
        confidence = min(1.0, len(matching_themes) * 0.3 + relationship_strength * 0.4)
        
        return {
            "authority": authority,
            "match_score": round(match_score, 2),
            "matching_themes": matching_themes,
            "confidence": round(confidence, 2),
            "effectiveness_rating": effectiveness
        }
    
    @staticmethod
    def recommend_authorities_for_subject(subject_id: str, top_n: int = 3) -> List[Dict]:
        """
        Recommend best authorities for a subject based on their risk profile.
        
        Returns list of top N authority recommendations with scores.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subject's authorities
        cursor.execute("SELECT * FROM authorities WHERE subject_id = ?", (subject_id,))
        authorities = cursor.fetchall()
        conn.close()
        
        if not authorities:
            return []
        
        # Extract themes from subject's content
        themes = AuthorityMatcher.extract_themes_from_posts(subject_id)
        
        # Score each authority
        recommendations = []
        for auth in authorities:
            # Map relationship strength
            relation_map = {
                "parent": 0.9,
                "guardian": 0.85,
                "therapist": 0.8,
                "mentor": 0.7,
                "teacher": 0.6,
                "coach": 0.65,
                "friend": 0.75,
                "religious guide": 0.7,
                "counselor": 0.75
            }
            
            relation_strength = relation_map.get(auth['relation'].lower(), 0.5)
            
            authority_dict = {
                "id": auth['id'],
                "name": auth['name'],
                "role": auth['role'],
                "relation": auth['relation']
            }
            
            score_result = AuthorityMatcher.score_authority_match(
                authority_dict,
                themes,
                relation_strength
            )
            
            recommendations.append(score_result)
        
        # Sort by match score (descending)
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Add detected themes to response
        result = {
            "subject_id": subject_id,
            "detected_themes": themes,
            "recommendations": recommendations[:top_n]
        }
        
        return result
