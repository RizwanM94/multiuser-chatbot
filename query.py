import subprocess
import chromadb
from sentence_transformers import SentenceTransformer
import time  # Added to store timestamps


# Initialize ChromaDB & embedding model
chroma_client = chromadb.PersistentClient(path="embeddings/")
collection = chroma_client.get_or_create_collection(name="pdf_data")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_relevant_chunks(query, user_id, top_k=3):
    """Retrieve top-k most relevant chunks for a specific user from ChromaDB."""
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    relevant_chunks = []
    for metadata in results["metadatas"][0]:
        if metadata.get("user_id") == user_id:
            relevant_chunks.append(metadata["text"])

    return relevant_chunks

def store_chat_history(user_id, question, answer):
    """Store the chat history in ChromaDB with user ID & timestamp for sorting."""
    timestamp = time.time()  # Unique timestamp
    collection.add(
        ids=[f"{user_id}_chat_{timestamp}"],  # Unique ID per chat entry
        embeddings=embedding_model.encode([question]).tolist(),
        metadatas=[{
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "timestamp": timestamp  # Store timestamp for sorting
        }]
    )

def get_chat_history(user_id):
    """Retrieve and sort chat history for a specific user."""
    results = collection.get(where={"user_id": user_id})

    chat_history = []
    for metadata in results["metadatas"]:
        if "question" in metadata and "answer" in metadata:
            chat_history.append((metadata["question"], metadata["answer"], metadata.get("timestamp", 0)))

    # Sort history by timestamp (oldest to newest)
    chat_history.sort(key=lambda x: x[2])

    return [(q, a) for q, a, _ in chat_history]  # Return question & answer only

def clear_user_chat_history(user_id):
    """Deletes all chat history for a specific user from ChromaDB."""
    # Filter and delete documents associated with the user_id
    collection.delete(where={"user_id": user_id})
    
def query_llama2(prompt):
    """Send a prompt to LLaMA 2 via Ollama."""
    cmd = ["ollama", "run", "llama2", prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()
