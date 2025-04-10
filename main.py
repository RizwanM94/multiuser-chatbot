import streamlit as st
import os
from auth import authenticate_user, logout_user
from process import extract_text_from_pdf, split_text, store_embeddings
from query import retrieve_relevant_chunks, store_chat_history, get_chat_history,clear_user_chat_history, query_llama2

st.set_page_config(page_title="RAG Chatbot", layout="wide")

user = authenticate_user()
if not user:
    st.stop()

user_id = user["email"]  # Use email as a unique identifier

st.sidebar.image(user["picture"], width=100)
st.sidebar.write(f"Hello, {user['name']}!")

if st.sidebar.button("Logout"):
    logout_user()

def clear_chat():
    """Clears user chat history from the database."""
    clear_user_chat_history(user_id)  # Function to delete history from DB
    st.success("Chat history cleared!")
    st.rerun()  # Refresh the page

# Add Clear Chat button in the sidebar
if st.sidebar.button("🗑️ Clear Chat History"):
    clear_chat()

st.title("Chat with Your Documents")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("PDF uploaded successfully!")

    text = extract_text_from_pdf("temp.pdf")
    chunks = split_text(text)
    store_embeddings(chunks, user_id)  # Store with user ID

    st.success("Document processed!")

# Retrieve previous chat history
st.subheader("Chat History")
chat_history = get_chat_history(user_id)

if chat_history:
    for chat in chat_history:
        st.write(f"**You:** {chat[0]}")  # User's question
        st.write(f"**Bot:** {chat[1]}")  # Bot's response
else:
    st.write("No previous chat history found.")  # Only shows if database is actually empty

# Chat input
user_input = st.text_input("Ask a question:")

if user_input:
    retrieved_chunks = retrieve_relevant_chunks(user_input, user_id)
    context = " ".join(retrieved_chunks)

    prompt = f"Using only the following context, answer the question:\n{context}\n\nQuestion: {user_input}"
    response = query_llama2(prompt)

    st.write("Chatbot:", response)

    # Store only user input and bot response
    store_chat_history(user_id, user_input, response)
