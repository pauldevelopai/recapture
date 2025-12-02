
import asyncio
import sys
import os

# Add backend to path
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.translation_service import translate_text, translate_input_to_english, translate_output_from_english

async def test_shona_support():
    print("🧪 Testing Shona Language Support\n")
    print("=" * 60)

    # Test 1: Direct Translation (Shona -> English -> Shona)
    print("📝 Test 1: Direct Translation (Shona -> English -> Shona)")
    original_text = "Mhoro, wakadii?" # Hello, how are you?
    print(f"Original (Shona): {original_text}")
    
    english_text = await translate_input_to_english(original_text, "sn")
    print(f"Translated to English: {english_text}")
    
    back_to_shona = await translate_output_from_english(english_text, "sn")
    print(f"Translated back to Shona: {back_to_shona}")
    print("-" * 60)
    
    print("\n✅ Shona Support Verification Complete")

if __name__ == "__main__":
    asyncio.run(test_shona_support())
