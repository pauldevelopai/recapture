from typing import List, Optional
from .models import DisinformationTrend
from .vector_store import query_documents
from .ai_service import client

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

async def chat_with_data(query: str) -> dict:
    """
    Answers a user query using RAG.
    Returns: { "response": str, "sources": list }
    """
    # 1. Retrieve Context
    retrieval_result = await retrieve_context_with_sources(query)
    context = retrieval_result["context_str"]
    sources = retrieval_result["sources"]
    
    # 2. Construct Prompt
    system_prompt = """You are a helpful assistant for the RECAPTURE application. 
    Your goal is to help users (parents, guardians) protect young people (Subjects) from radicalization.
    You have access to a knowledge base containing information about specific Subjects, their Authorities (influential figures), and active Disinformation Trends.
    
    Use the provided context to answer the user's question. 
    If the user asks about a specific Subject (e.g., "How is Alex doing?"), look for "Subject:" or "Profile:" entries in the context.
    If the answer is not in the context, use your general knowledge but mention that it's general advice.
    Be empathetic, practical, and solution-oriented.
    """
    
    user_prompt = f"""Context Information:
    {context}
    
    User Question: {query}
    """
    
    # 3. Call OpenAI
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return {
            "response": response.choices[0].message.content,
            "sources": sources
        }
    except Exception as e:
        return {
            "response": f"Error generating response: {str(e)}",
            "sources": []
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
