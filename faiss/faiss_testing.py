import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load a small, fast model to create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Sample data (Use sentences relevant to your campus project)
content = [
    "The library is located next to the Agora at the Bundoora campus.",
    "Students can find computer labs in the botanical building.",
    "The coffee shop is open from 8 AM to 5 PM daily.",
    "The 86 tram stops right outside the main university entrance."
]

# 3. Convert sentences to vectors
embeddings = model.encode(content)
dimension = embeddings.shape[1] # This model uses 384 dimensions

# 4. Initialize FAISS index (IndexFlatL2 is the best for beginners)
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype('float32'))

# 5. Test a search
query = "Where can I get caffeine?"
query_vector = model.encode([query])
k = 1  # Number of results to return
distances, indices = index.search(np.array(query_vector).astype('float32'), k)

print(f"Top Result: {content[indices[0][0]]}")