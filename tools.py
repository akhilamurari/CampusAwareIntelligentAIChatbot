from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def campus_rag_tool(query: str):
    """
    Searches the FAISS index for relevant information from campus PDFs.
    """
    # 1. Load the same embedding model we used in ingest_pdfs.py
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 2. Load the index from your data folder
    # allow_dangerous_deserialization is required for local .pkl files
    vector_db = FAISS.load_local(
        "data/campus_rag.index", 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    # 3. Perform a similarity search (k=3 fetches the top 3 most relevant chunks)
    docs = vector_db.similarity_search(query, k=3)
    
    # 4. Combine the chunks into one string to send to the LLM
    context = "\n---\n".join([doc.page_content for doc in docs])
    
    return context