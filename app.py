import streamlit as st
from rag_engine import process_document, ask_question

st.set_page_config(
    page_title="Document Chat",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Chat with your Document")
st.write("Upload a PDF and ask questions about it!")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None and st.session_state.vector_store is None:
    with st.spinner("Reading and processing document... 📖"):
        vector_store, num_chunks = process_document(uploaded_file)
        st.session_state.vector_store = vector_store
    st.success(f"Document processed into {num_chunks} chunks! Ask me anything about it 🚀")

if st.session_state.vector_store is not None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask a question about your document...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching document... 🔍"):
                answer = ask_question(st.session_state.vector_store, question)
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})