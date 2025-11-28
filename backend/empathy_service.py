"""
Empathy detection service using Hugging Face transformers.
Integrates empathy and emotion analysis into RAG and conversation systems.
"""

from typing import Dict, List, Optional
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
EMPATHY_MODEL_NAME = "bdotloh/roberta-base-empathy"
EMOTION_MODEL_NAME = "michellejieli/emotion_text_classifier"

# Global model cache
_empathy_pipeline = None
_emotion_pipeline = None


def load_empathy_model():
    """
    Load the RoBERTa-based empathy detection model from Hugging Face.
    Uses lazy loading and caching for performance.
    """
    global _empathy_pipeline
    
    if _empathy_pipeline is not None:
        return _empathy_pipeline
    
    try:
        from transformers import pipeline
        logger.info(f"Loading empathy model: {EMPATHY_MODEL_NAME}")
        _empathy_pipeline = pipeline(
            "text-classification",
            model=EMPATHY_MODEL_NAME,
            top_k=None  # Return all scores
        )
        logger.info("Empathy model loaded successfully")
        return _empathy_pipeline
    except Exception as e:
        logger.error(f"Failed to load empathy model: {e}")
        logger.warning("Empathy detection will be unavailable")
        return None


def load_emotion_model():
    """
    Load the emotion classification model for broader emotional analysis.
    """
    global _emotion_pipeline
    
    if _emotion_pipeline is not None:
        return _emotion_pipeline
    
    try:
        from transformers import pipeline
        logger.info(f"Loading emotion model: {EMOTION_MODEL_NAME}")
        _emotion_pipeline = pipeline(
            "text-classification",
            model=EMOTION_MODEL_NAME,
            top_k=None
        )
        logger.info("Emotion model loaded successfully")
        return _emotion_pipeline
    except Exception as e:
        logger.error(f"Failed to load emotion model: {e}")
        logger.warning("Emotion detection will be unavailable")
        return None


def detect_empathy(text: str) -> Dict[str, float]:
    """
    Analyze text for empathy and distress levels.
    
    Args:
        text: The input text to analyze
        
    Returns:
        dict with keys:
            - empathy_score: 0.0-1.0 (higher = more empathetic)
            - distress_score: 0.0-1.0 (higher = more distressed)
            - model_available: bool indicating if model loaded successfully
    """
    model = load_empathy_model()
    
    if model is None:
        return {
            "empathy_score": 0.5,
            "distress_score": 0.5,
            "model_available": False,
            "note": "Empathy model unavailable, using fallback"
        }
    
    try:
        results = model(text[:512])  # Limit to 512 tokens for RoBERTa
        
        # Parse results (format depends on model output)
        # bdotloh/roberta-base-empathy returns scores for empathy and distress
        scores = {}
        for item in results[0]:  # First result set
            label = item['label'].lower()
            score = item['score']
            scores[label] = score
        
        return {
            "empathy_score": scores.get('empathy', 0.5),
            "distress_score": scores.get('distress', 0.5),
            "model_available": True
        }
    except Exception as e:
        logger.error(f"Error detecting empathy: {e}")
        return {
            "empathy_score": 0.5,
            "distress_score": 0.5,
            "model_available": False,
            "error": str(e)
        }


def detect_emotions(text: str) -> Dict[str, float]:
    """
    Analyze text for broader emotional content.
    
    Args:
        text: The input text to analyze
        
    Returns:
        dict with emotion names as keys and confidence scores as values
        Also includes 'model_available' and 'dominant_emotion'
    """
    model = load_emotion_model()
    
    if model is None:
        return {
            "model_available": False,
            "note": "Emotion model unavailable"
        }
    
    try:
        results = model(text[:512])
        
        emotions = {}
        for item in results[0]:
            emotion = item['label'].lower()
            score = item['score']
            emotions[emotion] = score
        
        # Find dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1])
        
        return {
            **emotions,
            "dominant_emotion": dominant[0],
            "dominant_score": dominant[1],
            "model_available": True
        }
    except Exception as e:
        logger.error(f"Error detecting emotions: {e}")
        return {
            "model_available": False,
            "error": str(e)
        }


def analyze_conversation_empathy(messages: List[str]) -> Dict:
    """
    Analyze empathy levels across a conversation.
    
    Args:
        messages: List of message texts in chronological order
        
    Returns:
        dict with conversation-level empathy metrics
    """
    if not messages:
        return {
            "average_empathy": 0.5,
            "empathy_trend": "stable",
            "message_count": 0
        }
    
    empathy_scores = []
    for msg in messages:
        result = detect_empathy(msg)
        if result.get("model_available"):
            empathy_scores.append(result["empathy_score"])
    
    if not empathy_scores:
        return {
            "average_empathy": 0.5,
            "empathy_trend": "unknown",
            "message_count": len(messages),
            "note": "Model unavailable"
        }
    
    avg_empathy = sum(empathy_scores) / len(empathy_scores)
    
    # Determine trend (comparing first half vs second half)
    if len(empathy_scores) >= 4:
        mid = len(empathy_scores) // 2
        first_half_avg = sum(empathy_scores[:mid]) / mid
        second_half_avg = sum(empathy_scores[mid:]) / (len(empathy_scores) - mid)
        
        if second_half_avg > first_half_avg + 0.1:
            trend = "increasing"
        elif second_half_avg < first_half_avg - 0.1:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "average_empathy": avg_empathy,
        "empathy_trend": trend,
        "message_count": len(messages),
        "individual_scores": empathy_scores
    }


def suggest_empathetic_response(context: str, user_message: str) -> str:
    """
    Generate suggestions for making a response more empathetic.
    
    Args:
        context: Background context about the conversation
        user_message: The message to respond to
        
    Returns:
        String with empathy suggestions
    """
    # Analyze the user's emotional state
    empathy_result = detect_empathy(user_message)
    emotion_result = detect_emotions(user_message)
    
    suggestions = []
    
    # Check empathy level of incoming message
    if empathy_result.get("model_available"):
        if empathy_result["distress_score"] > 0.6:
            suggestions.append(
                "⚠️ High distress detected. Acknowledge their feelings first: "
                "'I can see this is really difficult for you...'"
            )
        
        if empathy_result["empathy_score"] < 0.3:
            suggestions.append(
                "💡 Low empathy in message. They may be defensive. Use validating language: "
                "'It makes sense you'd feel that way given...'"
            )
    
    # Check dominant emotion
    if emotion_result.get("model_available"):
        emotion = emotion_result.get("dominant_emotion", "")
        
        if emotion in ["anger", "disgust"]:
            suggestions.append(
                f"😤 {emotion.title()} detected. Don't argue directly. "
                "Try: 'I hear your frustration. Can we explore...'"
            )
        elif emotion in ["sadness", "fear"]:
            suggestions.append(
                f"😔 {emotion.title()} detected. Offer support: "
                "'This sounds overwhelming. You're not alone in this...'"
            )
        elif emotion == "joy":
            suggestions.append(
                "😊 Positive emotion detected. Build on it: "
                "'It's great that you're curious about this...'"
            )
    
    if not suggestions:
        suggestions.append(
            "💬 General tip: Start with validation, then gently introduce new perspectives."
        )
    
    return "\n".join(suggestions)


def get_empathy_guidance(empathy_score: float, distress_score: float) -> str:
    """
    Get guidance text based on empathy and distress scores.
    
    Args:
        empathy_score: 0-1 empathy level
        distress_score: 0-1 distress level
        
    Returns:
        Human-readable guidance string
    """
    if distress_score > 0.7:
        return "High distress - prioritize emotional support and safety"
    elif distress_score > 0.5:
        return "Moderate distress - acknowledge feelings before facts"
    elif empathy_score > 0.7:
        return "Empathetic communication - maintain this tone"
    elif empathy_score < 0.3:
        return "Low empathy - try more validating language"
    else:
        return "Balanced approach - continue with empathy"


# Preload models on module import (optional - comment out if causing startup issues)
# try:
#     load_empathy_model()
#     load_emotion_model()
# except Exception as e:
#     logger.warning(f"Could not preload models: {e}")
