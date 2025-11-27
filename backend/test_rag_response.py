"""
Test script to verify RAG query works correctly with seeded data.
"""
from vector_store import query_documents

def test_rag():
    print("🧪 Testing RAG Query Functionality...\n")
    
    queries = [
        "What is the blackpill ideology?",
        "What is accelerationism?",
        "How does radicalization happen?"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        results = query_documents(query, n_results=2)
        
        if results:
            print(f"✅ Found {len(results)} relevant documents:")
            for i, res in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"  Source: {res['metadata'].get('source', 'Unknown')}")
                print(f"  Type: {res['metadata'].get('type', 'Unknown')}")
                print(f"  Content Preview: {res['content'][:150]}...")
        else:
            print("❌ No results found")
        
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    test_rag()
