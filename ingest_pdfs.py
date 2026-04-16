import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_campus_rag():
    # AC: Create path for the documents folder
    docs_folder = "docs"
    index_path = "data/campus_rag.index"
    
    # Check if folder exists and has PDFs
    if not os.path.exists(docs_folder):
        print(f"Error: {docs_folder} folder not found.")
        return

    documents = []
    print("Step 1: Extracting text from PDFs using pypdf...")
    
    for file in os.listdir(docs_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(docs_folder, file)
            # AC: Extract text from PDFs using pypdf
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
            print(f" - Successfully loaded: {file}")

    if not documents:
        print("No PDFs found to process.")
        return

    # AC: Split text into chunks using LangChain text splitter
    print("Step 2: Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    print(f" - Created {len(chunks)} text chunks.")

    # AC: Generate embeddings and store in FAISS index
    print("Step 3: Generating embeddings (using HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Step 4: Building and saving FAISS index...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    # AC: Save index to data/campus_rag.index
    if not os.path.exists("data"):
        os.makedirs("data")
    
    vector_db.save_local(index_path)
    print(f"✅ SUCCESS: Index saved to {index_path}")

if __name__ == "__main__":
    build_campus_rag()