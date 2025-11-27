import chromadb
import os
from chromadb.utils import embedding_functions
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Initialize ChromaDB Client
# Using persistent storage so data survives restarts
client = chromadb.PersistentClient(path="./chroma_db")

# Use OpenAI Embedding Function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Get or Create Collection
collection = client.get_or_create_collection(
    name="recapture_knowledge_base",
    embedding_function=openai_ef
)

def add_documents(documents: List[str], metadatas: List[Dict], ids: List[str]):
    """
    Adds documents to the vector store.
    """
    try:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully added {len(documents)} documents to vector store.")
    except Exception as e:
        print(f"Error adding documents: {e}")

def query_documents(query_text: str, n_results: int = 5) -> List[Dict]:
    """
    Queries the vector store for relevant documents.
    """
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Flatten results
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        combined_results = []
        for doc, meta in zip(documents, metadatas):
            combined_results.append({
                "content": doc,
                "metadata": meta
            })
            
        return combined_results
    except Exception as e:
        print(f"Error querying documents: {e}")
        return []

def clear_collection():
    """
    Clears the collection (useful for re-seeding).
    """
    try:
        client.delete_collection("recapture_knowledge_base")
        # Re-create
        global collection
        collection = client.get_or_create_collection(
            name="recapture_knowledge_base",
            embedding_function=openai_ef
        )
        print("Collection cleared.")
    except Exception as e:
        print(f"Error clearing collection: {e}")

def get_collection_stats() -> Dict:
    """
    Returns statistics about the vector store collection.
    """
    try:
        count = collection.count()
        return {
            "total_documents": count,
            "collection_name": "recapture_knowledge_base"
        }
    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {"total_documents": 0, "collection_name": "recapture_knowledge_base"}

def get_all_documents(limit: int = 100, offset: int = 0) -> List[Dict]:
    """
    Retrieves all documents from the vector store with pagination.
    """
    try:
        results = collection.get(
            limit=limit,
            offset=offset,
            include=['documents', 'metadatas']
        )
        
        combined_results = []
        if results['ids']:
            for i in range(len(results['ids'])):
                combined_results.append({
                    "id": results['ids'][i],
                    "content": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })
                
        return combined_results
    except Exception as e:
        print(f"Error getting all documents: {e}")
        return []
