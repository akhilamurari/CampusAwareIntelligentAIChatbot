from tools import campus_rag_tool

# Test with a question related to the PDFs you uploaded
question = "Where is the Melbourne Bundoora campus located?"
print(f"Testing RAG with question: {question}")

result = campus_rag_tool(question)

print("\n--- Search Results from PDFs ---")
print(result)
