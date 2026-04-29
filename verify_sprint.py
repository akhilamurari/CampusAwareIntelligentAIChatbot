import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from src.tools import campus_rag_tool

# The 10 validation questions for Sprint 4
test_queries = [
    "What is the daily maximum fee for a White parking bay?",
    "When is the UniSafe escort service available?",
    "What are the face-to-face library support hours at Bundoora?",
    "What is the emergency phone number for Campus Security?",
    "What is the CRICOS code for the Master of Information and Communication Technology?",
    "What are the rules for overnight guests in student residence?",
    "What is the total credit points required for the Master of ICT?",
    "What is the address of the Melbourne Bundoora campus?",
    "What app is used for parking payments at La Trobe?",
    "Is there a free bus service like the Glider on campus?",
    "What is the definition of Criterion-based assessment?",
    "What is considered a privacy data breach at La Trobe?",
    "What are the consequences of breaching the Code of Conduct?"
]

# ... (imports and queries stay the same)

print(f"{'#'*60}\nSPRINT 5 VALIDATION REPORT\n{'#'*60}")

for i, query in enumerate(test_queries, 1):
    print(f"\n[TEST {i}] {query.upper()}")
    try:
        # 1. Get the raw result
        raw_result = campus_rag_tool.invoke(query)
        
        # 2. Clean the output: 
        # Replace multiple newlines/spaces with a single space
        clean_result = " ".join(raw_result.split())
        
        # 3. Limit to first 300 characters for readability
        print(f"FOUND: {clean_result[:1000]}...")
        print("-" * 30)
        
    except Exception as e:
        print(f"[ERROR]: {e}")

print(f"\n{'#'*60}\nVALIDATION COMPLETE\n{'#'*60}")
