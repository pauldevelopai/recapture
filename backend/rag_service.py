from typing import List, Optional
from .models import DisinformationTrend
from .vector_store import query_documents
from .ai_service import client
from .empathy_service import detect_empathy, detect_emotions, suggest_empathetic_response
from .translation_service import translate_input_to_english, translate_output_from_english

async def retrieve_context_with_sources(query: str) -> dict:
    """
    Retrieves relevant documents from the vector store.
    Returns a dict with formatted context string and raw sources.
    """
    results = query_documents(query, n_results=3)
    
    if not results:
        return {"context_str": "", "sources": []}
        
    context_str = "\n\n".join([
        f"--- Document ({r['metadata']['type']}) ---\n{r['content']}" 
        for r in results
    ])
    
    sources = []
    for r in results:
        source_info = {
            "type": r['metadata'].get('type', 'unknown'),
            "content": r['content'],
            "metadata": r['metadata']
        }
        sources.append(source_info)
    
    return {"context_str": context_str, "sources": sources}

async def retrieve_context(query: str) -> str:
    """
    Wrapper for backward compatibility. Returns just the context string.
    """
    result = await retrieve_context_with_sources(query)
    return result["context_str"]

async def chat_with_data(query: str, language: str = "en") -> dict:
    """
    Answers a user query using RAG with empathy detection and translation support.
    Returns: { "response": str, "sources": list, "empathy_analysis": dict }
    """
    # 0. Translate input if needed
    processed_query = await translate_input_to_english(query, language)
    
    # 1. Analyze query for emotional content (on English text)
    empathy_result = detect_empathy(processed_query)
    emotion_result = detect_emotions(processed_query)
    
    # 2. Retrieve Context
    retrieval_result = await retrieve_context_with_sources(processed_query)
    context = retrieval_result["context_str"]
    sources = retrieval_result["sources"]
    
    # 3. Construct empathy-aware prompt
    system_prompt = """You are a helpful assistant for the RECAPTURE application. 
    Your goal is to help users (parents, guardians) protect young people (Subjects) from radicalization.
    You have access to a knowledge base containing information about specific Subjects, their Authorities (influential figures), and active Disinformation Trends.
    
    Use the provided context to answer the user's question. 
    If the user asks about a specific Subject (e.g., "How is Alex doing?"), look for "Subject:" or "Profile:" entries in the context.
    If the answer is not in the context, use your general knowledge but mention that it's general advice.
    Be empathetic, practical, and solution-oriented.
    """
    
    # Adjust system prompt based on emotional state
    if empathy_result.get("model_available"):
        distress_score = empathy_result.get("distress_score", 0.5)
        empathy_score = empathy_result.get("empathy_score", 0.5)
        
        if distress_score > 0.6:
            system_prompt += "\n\nIMPORTANT: The user appears distressed. Prioritize emotional support and validation before providing factual information."
        elif empathy_score < 0.3:
            system_prompt += "\n\nIMPORTANT: The user's query lacks empathetic language. Model compassionate communication in your response."
    
    if emotion_result.get("model_available"):
        dominant_emotion = emotion_result.get("dominant_emotion", "")
        if dominant_emotion in ["anger", "fear", "sadness"]:
            system_prompt += f"\n\nThe user seems to be feeling {dominant_emotion}. Acknowledge this emotion gently in your response."
    
    user_prompt = f"""Context Information:
    {context}
    
    User Question: {query}
    """
    
    # 4. Call OpenAI
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        english_response = response.choices[0].message.content
        final_response = await translate_output_from_english(english_response, language)
        
        return {
            "response": final_response,
            "sources": sources,
            "empathy_analysis": {
                "query_empathy": empathy_result.get("empathy_score"),
                "query_distress": empathy_result.get("distress_score"),
                "dominant_emotion": emotion_result.get("dominant_emotion"),
                "empathy_guidance": suggest_empathetic_response(context, processed_query)
            }
        }
    except Exception as e:
        return {
            "response": f"Error generating response: {str(e)}",
            "sources": [],
            "empathy_analysis": {}
        }

async def augment_analysis_with_context(text: str, base_analysis: dict) -> dict:
    """
    Enhances the base analysis with context from the knowledge base.
    """
    # Simple RAG for analysis enhancement
    # We can query the vector store for similar harmful content
    results = query_documents(text, n_results=2)
    
    if results:
        base_analysis["context_notes"] = [
            f"Similar content found: {r['content'][:100]}..." for r in results
        ]
    
    return base_analysis
