"""
Translation service for handling multi-language support.
Uses OpenAI to translate between English and target African languages.
"""

import os
from typing import Optional
import logging
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPPORTED_LANGUAGES = {
    "en": "English",
    "sw": "Swahili",
    "zu": "Zulu",
    "xh": "Xhosa",
    "yo": "Yoruba",
    "ig": "Igbo",
    "ha": "Hausa",
    "am": "Amharic",
    "so": "Somali",
    "sn": "Shona",
    "af": "Afrikaans",
    "om": "Oromo",
    "rw": "Kinyarwanda",
    "tw": "Twi",
    "st": "Sesotho"
}

async def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """
    Translate text to the target language using OpenAI.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'zu', 'sw')
        source_lang: Source language code (default 'auto')
        
    Returns:
        Translated text
    """
    if not text or not text.strip():
        return ""
        
    # If target is English and source is English (or auto and text looks English), 
    # we might skip, but for now let's rely on the caller to check if translation is needed.
    if target_lang == "en" and source_lang == "en":
        return text

    target_lang_name = SUPPORTED_LANGUAGES.get(target_lang, target_lang)
    
    system_prompt = f"""You are a professional translator. 
    Translate the following text into {target_lang_name}.
    Maintain the tone, nuance, and emotional context of the original text.
    If the text is technical or specific to the Recapture application context (radicalization, social media), ensure accurate terminology.
    Return ONLY the translated text, no introductory or concluding remarks.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        translated_text = response.choices[0].message.content.strip()
        return translated_text
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        # Fallback: return original text if translation fails
        return text

async def translate_input_to_english(text: str, source_lang: str) -> str:
    """Helper to translate user input to English for processing"""
    if source_lang == "en":
        return text
    return await translate_text(text, "en", source_lang)

async def translate_output_from_english(text: str, target_lang: str) -> str:
    """Helper to translate system output from English to user's language"""
    if target_lang == "en":
        return text
    return await translate_text(text, target_lang, "en")
