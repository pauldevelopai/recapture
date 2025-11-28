"""
Test script for empathy detection service.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from empathy_service import (
    detect_empathy,
    detect_emotions,
    analyze_conversation_empathy,
    suggest_empathetic_response,
    get_empathy_guidance
)


def test_empathy_detection():
    print("🧪 Testing Empathy Detection Service\n")
    print("=" * 60)
    
    test_texts = [
        {
            "name": "High Empathy",
            "text": "I can really understand how you're feeling. I've been there too, and I know this must be incredibly difficult for you. Please know that I'm here to support you."
        },
        {
            "name": "Low Empathy",
            "text": "You're just wrong about this. The facts clearly show otherwise."
        },
        {
            "name": "High Distress",
            "text": "I can't take this anymore. Everything feels hopeless and I don't know what to do. I'm so overwhelmed."
        },
        {
            "name": "Angry Tone",
            "text": "This is absolutely ridiculous! I'm so tired of being told what to think. Nobody understands what I'm going through!"
        },
        {
            "name": "Neutral",
            "text": "Can you explain what you mean by that? I'm interested in learning more about this topic."
        }
    ]
    
    for test in test_texts:
        print(f"\n📝 Test: {test['name']}")
        print(f"Text: \"{test['text'][:60]}...\"")
        print("-" * 60)
        
        # Test empathy detection
        empathy_result = detect_empathy(test['text'])
        print(f"✓ Empathy Detection:")
        print(f"  - Empathy Score: {empathy_result.get('empathy_score', 'N/A')}")
        print(f"  - Distress Score: {empathy_result.get('distress_score', 'N/A')}")
        print(f"  - Model Available: {empathy_result.get('model_available', False)}")
        
        # Test emotion detection
        emotion_result = detect_emotions(test['text'])
        print(f"✓ Emotion Detection:")
        if emotion_result.get('model_available'):
            print(f"  - Dominant Emotion: {emotion_result.get('dominant_emotion', 'N/A')}")
            print(f"  - Confidence: {emotion_result.get('dominant_score', 'N/A'):.2f}")
        else:
            print(f"  - Model Unavailable")
        
        # Test empathy guidance
        if empathy_result.get('model_available'):
            guidance = get_empathy_guidance(
                empathy_result.get('empathy_score', 0.5),
                empathy_result.get('distress_score', 0.5)
            )
            print(f"✓ Guidance: {guidance}")
    
    print("\n" + "=" * 60)
    print("🧪 Testing Conversation Analysis\n")
    
    # Test conversation empathy
    conversation = [
        "You're completely wrong and you don't understand anything.",
        "I see where you're coming from, but have you considered this perspective?",
        "I appreciate your patience with me. This is helping me think differently.",
        "Thank you for understanding. I feel like I can trust you."
    ]
    
    conv_result = analyze_conversation_empathy(conversation)
    print(f"Average Empathy: {conv_result.get('average_empathy', 'N/A')}")
    print(f"Empathy Trend: {conv_result.get('empathy_trend', 'N/A')}")
    print(f"Message Count: {conv_result.get('message_count', 0)}")
    
    if conv_result.get('individual_scores'):
        print("\nIndividual Scores:")
        for i, score in enumerate(conv_result['individual_scores'], 1):
            print(f"  Message {i}: {score:.2f}")
    
    print("\n" + "=" * 60)
    print("🧪 Testing Empathetic Response Suggestions\n")
    
    test_message = "I'm really struggling with this and feel like nobody cares about what I think."
    suggestions = suggest_empathetic_response("Counter-radicalization conversation", test_message)
    print(f"Message: \"{test_message}\"")
    print(f"\nSuggestions:\n{suggestions}")
    
    print("\n" + "=" * 60)
    print("✅ All empathy service tests completed!\n")


if __name__ == "__main__":
    test_empathy_detection()
