import asyncio
import json
import os
import sys
from translation_service import translate_text, SUPPORTED_LANGUAGES

# Path to translations directory
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'src', 'translations')
EN_FILE = os.path.join(TRANSLATIONS_DIR, 'en.json')

async def translate_recursive(data, target_lang):
    if isinstance(data, dict):
        return {k: await translate_recursive(v, target_lang) for k, v in data.items()}
    elif isinstance(data, str):
        print(f"Translating: {data[:30]}... to {target_lang}")
        return await translate_text(data, target_lang, source_lang='en')
    else:
        return data

async def main():
    # Load English translations
    with open(EN_FILE, 'r') as f:
        en_data = json.load(f)

    # Iterate over supported languages
    for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
        if lang_code == 'en':
            continue

        print(f"Processing {lang_name} ({lang_code})...")
        target_file = os.path.join(TRANSLATIONS_DIR, f'{lang_code}.json')
        
        # Check if file exists to avoid re-translating everything (optional, but good for now I'll overwrite to ensure freshness)
        # Actually, let's overwrite to ensure we get the new strings.
        
        translated_data = await translate_recursive(en_data, lang_code)
        
        with open(target_file, 'w') as f:
            json.dump(translated_data, f, indent=4, ensure_ascii=False)
        
        print(f"Saved {lang_name} translations to {target_file}")

if __name__ == "__main__":
    asyncio.run(main())
