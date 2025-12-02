
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.translation_service import translate_text, translate_input_to_english, translate_output_from_english

async def test_new_languages():
    print("🧪 Testing New African Languages Support\n")
    print("=" * 60)

    test_cases = [
        {"lang": "om", "name": "Oromo", "text": "Akkam, fayyaa?"}, # Hello, how are you?
        {"lang": "rw", "name": "Kinyarwanda", "text": "Muraho, amakuru?"}, # Hello, how are you?
        {"lang": "tw", "name": "Twi", "text": "Ete sen?"}, # How is it? (Hello)
        {"lang": "st", "name": "Sesotho", "text": "Dumela, o kae?"} # Hello, how are you?
    ]

    for case in test_cases:
        lang_code = case["lang"]
        lang_name = case["name"]
        original_text = case["text"]

        print(f"📝 Testing {lang_name} ({lang_code})")
        print(f"Original: {original_text}")
        
        # Translate to English
        english_text = await translate_input_to_english(original_text, lang_code)
        print(f"To English: {english_text}")
        
        # Translate back to Target Language
        back_to_lang = await translate_output_from_english(english_text, lang_code)
        print(f"Back to {lang_name}: {back_to_lang}")
        print("-" * 60)
    
    print("\n✅ New Languages Verification Complete")

if __name__ == "__main__":
    asyncio.run(test_new_languages())
