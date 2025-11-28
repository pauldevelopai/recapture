"""
Test script for verifying African language support via translation layer.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.translation_service import translate_text, translate_input_to_english, translate_output_from_english
from backend.rag_service import chat_with_data
from backend.digital_clone_service import chat_with_clone

async def test_translation_flow():
    print("🧪 Testing African Language Support\n")
    print("=" * 60)

    # Test 1: Direct Translation Service
    print("📝 Test 1: Direct Translation (Zulu -> English -> Zulu)")
    original_text = "Sawubona, ngicela ungisize." # Hello, please help me.
    print(f"Original (Zulu): {original_text}")
    
    english_text = await translate_input_to_english(original_text, "zu")
    print(f"Translated to English: {english_text}")
    
    back_to_zulu = await translate_output_from_english(english_text, "zu")
    print(f"Translated back to Zulu: {back_to_zulu}")
    print("-" * 60)

    # Test 2: RAG Chat in Swahili
    print("\n📝 Test 2: RAG Chat in Swahili")
    swahili_query = "Je, ni nini dalili za itikadi kali?" # What are the signs of radicalization?
    print(f"Query (Swahili): {swahili_query}")
    
    # Mocking RAG response for speed/cost if needed, but let's try real flow
    try:
        rag_result = await chat_with_data(swahili_query, language="sw")
        print(f"RAG Response (Swahili): {rag_result['response'][:150]}...")
        
        if "empathy_analysis" in rag_result:
            print("✅ Empathy Analysis included (performed on English translation)")
        else:
            print("❌ Empathy Analysis missing")
            
    except Exception as e:
        print(f"❌ RAG Test Failed: {e}")

    print("-" * 60)
    
    print("\n✅ Translation Flow Verification Complete")

if __name__ == "__main__":
    asyncio.run(test_translation_flow())
