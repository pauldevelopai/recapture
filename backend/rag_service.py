from typing import List, Optional
from .models import DisinformationTrend
from .vector_store import query_documents
from .ai_service import client

async def retrieve_context(query: str) -> str:
    """
    Retrieves relevant documents from the vector store.
    Returns a formatted string of context.
    """
    results = query_documents(query, n_results=3)
    
    if not results:
        return ""
        
    context_str = "\n\n".join([
        f"--- Document ({r['metadata']['type']}) ---\n{r['content']}" 
        for r in results
    ])
    
    return context_str

async def chat_with_data(query: str) -> str:
    """
    Answers a user query using RAG.
    """
    # 1. Retrieve Context
    context = await retrieve_context(query)
    
    # 2. Construct Prompt
    system_prompt = """You are a helpful assistant for the RECAPTURE application. 
    Your goal is to help users (parents, guardians) protect young people from radicalization.
    Use the provided context to answer the user's question. 
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
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

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
