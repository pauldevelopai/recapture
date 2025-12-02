
import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rag_service import chat_with_data

async def test_rag_quality():
    print("🧪 Testing RAG Chat Quality\n")
    print("=" * 60)

    test_queries = [
        "What are the common signs of radicalization in teenagers?",
        "I found my son watching videos about the 'Great Replacement'. What should I do?",
        "How can I talk to my daughter who is angry at the government?",
        "Tell me about the 'Incel' ideology trends."
    ]

    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 30)
        
        try:
            result = await chat_with_data(query)
            
            # Print Empathy Analysis
            empathy = result.get("empathy_analysis", {})
            print(f"❤️ Empathy Score: {empathy.get('query_empathy')}")
            print(f"😫 Distress Score: {empathy.get('query_distress')}")
            print(f"😡 Dominant Emotion: {empathy.get('dominant_emotion')}")
            
            # Print Sources (Context)
            sources = result.get("sources", [])
            print(f"\n📚 Sources Found: {len(sources)}")
            for i, source in enumerate(sources):
                content_preview = source['content'][:100].replace('\n', ' ')
                print(f"   {i+1}. [{source['type']}] {content_preview}...")

            # Print Response
            print(f"\n🤖 Response:\n{result['response']}")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag_quality())
