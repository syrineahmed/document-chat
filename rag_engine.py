from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os
import fitz

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

def create_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_text(text)
    return chunks

def build_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_texts(chunks, embeddings)
    return vector_store

def process_document(file):
    text = extract_text_from_pdf(file)
    chunks = create_chunks(text)
    vector_store = build_vector_store(chunks)
    return vector_store, len(chunks)

def ask_question(vector_store, question):
    relevant_chunks = vector_store.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in relevant_chunks])
    
    prompt = f"""
    Answer the question based ONLY on the following context from the document.
    If the answer is not in the context, say "I cannot find this information in the document."
    
    CONTEXT:
    {context}
    
    QUESTION:
    {question}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content