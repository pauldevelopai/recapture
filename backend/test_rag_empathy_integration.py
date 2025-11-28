import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.rag_service import chat_with_data
from backend.empathy_service import detect_empathy

async def test_rag_empathy_flow():
    print("🧪 Testing RAG + Empathy Integration\n")
    print("=" * 60)

    # Test Case 1: Distressed Query
    query_distressed = "I'm really scared that my brother is getting involved with these dangerous groups. I don't know what to do and I feel helpless."
    print(f"📝 Test Query 1 (Distressed): \"{query_distressed}\"")
    
    response_distressed = await chat_with_data(query_distressed)
    
    print("\n🔍 Analysis Results:")
    if "empathy_analysis" in response_distressed:
        ea = response_distressed["empathy_analysis"]
        print(f"  - Query Empathy Score: {ea.get('query_empathy')}")
        print(f"  - Query Distress Score: {ea.get('query_distress')}")
        print(f"  - Dominant Emotion: {ea.get('dominant_emotion')}")
        print(f"  - Guidance: {ea.get('empathy_guidance')}")
    else:
        print("  ❌ 'empathy_analysis' missing from response!")

    print(f"\n🤖 AI Response Preview:\n  \"{response_distressed['response'][:150]}...\"")
    
    # Check if response actually acknowledges the distress (heuristic check)
    response_text_lower = response_distressed['response'].lower()
    if any(word in response_text_lower for word in ["understand", "scary", "difficult", "support", "help", "sorry"]):
        print("\n✅ Response appears to contain empathetic language.")
    else:
        print("\n⚠️ Response might lack empathetic language.")

    print("-" * 60)

    # Test Case 2: Factual/Neutral Query
    query_factual = "What are the common symbols used by the 'Order of Nine Angles'?"
    print(f"\n📝 Test Query 2 (Factual): \"{query_factual}\"")
    
    response_factual = await chat_with_data(query_factual)
    
    print("\n🔍 Analysis Results:")
    if "empathy_analysis" in response_factual:
        ea = response_factual["empathy_analysis"]
        print(f"  - Query Empathy Score: {ea.get('query_empathy')}")
        print(f"  - Query Distress Score: {ea.get('query_distress')}")
    else:
        print("  ❌ 'empathy_analysis' missing from response!")

    print(f"\n🤖 AI Response Preview:\n  \"{response_factual['response'][:150]}...\"")
    
    # Verify Sources are returned (Basic RAG check)
    if response_factual.get('sources'):
        print(f"\n✅ Retrieved {len(response_factual['sources'])} sources from Knowledge Base.")
    else:
        print("\n⚠️ No sources retrieved. (Vector store might be empty or query found no matches)")

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_rag_empathy_flow())
