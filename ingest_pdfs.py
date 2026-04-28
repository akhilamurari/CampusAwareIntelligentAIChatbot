import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_campus_rag():
    # AC: Create path for the documents folder
    docs_folder = "docs"
    index_path = "data/campus_rag.index"
    
    # Check if folder exists
    if not os.path.exists(docs_folder):
        print(f"Error: {docs_folder} folder not found.")
        return

    documents = []
    print("Step 1: Extracting text from docs/ folder...")

    for file in os.listdir(docs_folder):
        file_path = os.path.join(docs_folder, file)

        if file.endswith(".pdf"):
            try:
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
                print(f"  [PDF] Loaded: {file}")
            except Exception as e:
                print(f"  [PDF] Failed to load {file}: {e}")

        elif file.endswith(".txt"):
            try:
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())
                print(f"  [TXT] Loaded: {file}")
            except Exception as e:
                print(f"  [TXT] Failed to load {file}: {e}")

    if not documents:
        print("No documents found to process.")
        return

    print(f"\n  Total documents loaded: {len(documents)}")

    # AC: Split text into chunks using LangChain text splitter
    print("\nStep 2: Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  Created {len(chunks)} text chunks.")

    # AC: Generate embeddings and store in FAISS index
    print("\nStep 3: Generating embeddings (using HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("\nStep 4: Building and saving FAISS index...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    # AC: Save index to data/campus_rag.index
    if not os.path.exists("data"):
        os.makedirs("data")

    vector_db.save_local(index_path)
    print(f"\n✅ SUCCESS: Index saved to {index_path}")
    print(f"   Total chunks indexed: {len(chunks)}")

if __name__ == "__main__":
    build_campus_rag()