import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from extract_text import extract_text_from_pdf
import os

# Initialize ChromaDB
os.environ["TOKENIZERS_PARALLELISM"] = "false"
chroma_client = chromadb.PersistentClient(path="embeddings/")
collection = chroma_client.get_or_create_collection(name="pdf_data")

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def split_text(text, chunk_size=500, chunk_overlap=50):
    """Split text into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)

def store_embeddings(chunks, user_id):
    """Convert text chunks into embeddings and store in ChromaDB."""
    embeddings = embedding_model.encode(chunks).tolist()

    for i, chunk in enumerate(chunks):
        unique_id = f"{user_id}_chunk_{i}"  
        collection.add(
            ids=[unique_id],  
            embeddings=[embeddings[i]],
            metadatas=[{"text": chunk, "user_id": user_id}]
        )

    print(f"Embeddings stored for user {user_id}!")
