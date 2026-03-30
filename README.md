# Campus-Aware Intelligent AI Agent
AI-powered chatbot for La Trobe University Bundoora campus.
Ask anything about campus data in plain English.

## Team
Akhila | Tarun | Harshitha | Ben | Jince | Ansu

## Tech Stack
NVIDIA NIM · LangChain · LangGraph · Streamlit · SQLite · FAISS

## Setup
1. Clone the repo
2. Run: docker-compose up
3. Open: http://localhost:8501

## Supervisors
Dr Di Wu & Phu Lai — Cisco–La Trobe Centre for AI & IoT
```

**3. Set up branching strategy**
Tell the team — **never push directly to main!**
```
main          → stable working code only
develop       → team merges all features here
feature/xxx   → each person works on their own branch

Example branches:
feature/streamlit-ui        (Tarun)
feature/nvidia-nim          (Ansu)
feature/langgraph-agent     (Jince)
feature/docker-setup        (Akhila)
feature/synthetic-data      (Harshitha)
feature/faiss-research      (Ben)