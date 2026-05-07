# CampusAware Intelligent AI Agent
### Cisco-La Trobe University AI & IoT Centre

An on-premises campus assistant chatbot for La Trobe University's Bundoora campus, powered by real-time IoT sensor data and campus document retrieval. Ask anything about campus room conditions, facilities, policies and course information in plain English.

---

##  Key Results
- **SUS Score:** 87/100 (Excellent)
- **Response Time:** 1.8 seconds (on-premises)
- **NL2SQL Accuracy:** 100%
- **RAG Accuracy:** 100%
- **User Rating:** 10/10 Excellent ⭐⭐⭐⭐⭐

---

##  What Can It Do?

### Room Conditions (NL2SQL)
```
"Which room had the highest CO2 levels?"
"Find me a quiet room to study"
"What is the average temperature in the library?"
"Which rooms are currently occupied?"
"What is the air quality in Lab-101?"
```

### Campus Information (RAG)
```
"How do I connect to eduroam WiFi?"
"What are the library opening hours?"
"What is the after hours helpline number?"
"What is the CRICOS code for Master of ICT?"
"How much is daily parking?"
```

---

## 🌐 Public Access

The app is permanently deployed on the Cisco server!

**Just open this URL in any browser:**
```
https://glorify-overcome-provoke.ngrok-free.dev
```
No setup, no installation, no SSH needed! 

If you see a warning page — click **"Visit Site"** to proceed.

---

##  Architecture

```
Student Browser
      ↓
ngrok Public URL
      ↓
Streamlit UI (app.py) — running on aiotcentre-03
      ↓
LangGraph Agent (agent.py)
      ↓
┌─────────────────────────────────┐
│  campus_db_tool  |  campus_rag_tool  │
└─────────────────────────────────┘
      ↓                    ↓
SQLite IoT DB          FAISS Vector Store
      ↓
Qwen2.5-7B-Instruct (vLLM)
aiotcentre-03 — 4x NVIDIA L40S GPUs
```

---

##  Tech Stack

| Component | Technology |
|---|---|
| LLM | Qwen2.5-7B-Instruct via vLLM |
| Agent Framework | LangGraph + LangChain |
| UI | Streamlit |
| Database | SQLite (48,960 simulated IoT records) |
| Vector Store | FAISS (246 chunks) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Server | aiotcentre-03 (4x NVIDIA L40S 46GB) |
| Public Access | ngrok |

---

##  Prerequisites (Local Development Only)

- Python 3.11+
- Mac/Linux
- La Trobe VPN (GlobalProtect) for server access
- ngrok account (free)

---

##  Setup (One Time Only — Local Development)

### 1. Clone the repo
```bash
git clone https://github.com/akhilamurari/CampusAwareIntelligentAIChatbot.git
cd CampusAwareIntelligentAIChatbot
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create .env file
```bash
cp .env.example .env
nano .env
```

Add these values:
```
NIM_MODE=onprem
NIM_BASE_URL_ONPREM=http://localhost:8000/v1
NIM_MODEL=/data/shared/nobackup/Qwen2.5-7B-Instruct
NIM_API_KEY=not-required
NVIDIA_API_KEY=not-required
```

### 4. Install ngrok
```bash
brew install ngrok
ngrok config add-authtoken YOUR_TOKEN
```

---

## ▶ Running the App

### For Users (Students & Team)
The app is permanently deployed — just open the URL:
```
https://glorify-overcome-provoke.ngrok-free.dev
```

---

### For Developers (Local Development)

You need **3 terminal tabs:**

#### Tab 1 — SSH into Server + SSH Tunnel
```bash
# Terminal 1 — SSH into server
ssh -p 6022 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au

# Terminal 2 — SSH tunnel
ssh -p 6022 -L 8000:localhost:8000 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au
```

#### Tab 3 — Run App Locally
```bash
cd CampusAwareIntelligentAIChatbot
source venv/bin/activate
./start_app.sh
```

---

## 🖥️ Server Sessions (aiotcentre-03)

All three components run persistently via tmux — no manual setup needed:

| Session | Component | Port |
|---|---|---|
| vllm | Qwen2.5-7B-Instruct via vLLM | 8000 |
| app | Streamlit web interface | 8502 |
| ngrok | Public URL tunnel | — |

### Check server status
```bash
ssh -p 6022 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au
tmux ls
```

### Restart everything if server reboots
```bash
# vLLM
tmux new-session -d -s vllm
tmux send-keys -t vllm "source ~/miniconda3/bin/activate && CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server --model /data/shared/nobackup/Qwen2.5-7B-Instruct --port 8000 --dtype bfloat16 --gpu-memory-utilization 0.65 --max-model-len 4096 --enable-auto-tool-choice --tool-call-parser hermes" Enter

# Streamlit
tmux new-session -d -s app
tmux send-keys -t app "cd ~/CampusAwareIntelligentAIChatbot && source venv/bin/activate && streamlit run app.py --server.port 8502 --server.address 0.0.0.0" Enter

# ngrok
tmux new-session -d -s ngrok
tmux send-keys -t ngrok "cd ~/CampusAwareIntelligentAIChatbot && ./ngrok http 8502" Enter
```

### Check ngrok URL
```bash
curl http://localhost:4040/api/tunnels
```

---

## 🗄️ Database

### Simulated IoT Sensor Data
- **17 rooms** monitored
- **48,960 records** (30 days, 15-minute intervals)
- **Sensors:** temperature, humidity, CO2, noise, light, occupancy, air quality

### Rooms
```
Libraries:     Library-L1, Library-L2, Library-L3
Labs:          Lab-101, Lab-102, Lab-203, Lab-301, Lab-302
Lecture Halls: Lecture-Hall-A, Lecture-Hall-B, Lecture-Hall-C
Study Rooms:   Study-Room-1, Study-Room-2, Study-Room-3
Other:         Cafeteria, Meeting-Room-1, Student-Lounge
```

### Regenerate Database
```bash
python generate_iot_data.py
python load_to_sqlite.py
```

---

##  Knowledge Base

### PDFs Ingested (246 chunks)
1. Melbourne Campus Map
2. Library Opening Hours
3. La Trobe Student Safety Guide
4. Rules of Residence 2026
5. Fees and Permits, Car Parking
6. Master of ICT Handbook
7. Student Charter
8. Student Support Policy
9. Admissions Policy
10. Code of Conduct

### Re-ingest PDFs
```bash
python ingest_pdfs.py
```

---

##  Testing

### Run Agent Tests (requires vLLM server running)
```bash
source venv/bin/activate
python -m pytest tests/test_agent.py -v
```

Expected output:
```
✅ test_agent_nl2sql_connection PASSED
✅ test_agent_rag_retrieval PASSED
✅ test_agent_rag_retrieval_specifically PASSED
✅ test_agent_multi_turn PASSED
4 passed in ~10s
```

### Run CI Tests (no server needed)
```bash
python -m pytest tests/test_ci.py -v
```

---

##  Project Structure

```
CampusAwareIntelligentAIChatbot/
├── app.py                  # Streamlit UI
├── agent.py                # LangGraph agent runner
├── start_app.sh            # Startup script (local development)
├── generate_iot_data.py    # IoT data generator
├── load_to_sqlite.py       # Load CSV to SQLite
├── ingest_pdfs.py          # PDF to FAISS ingestion
├── ragas_eval.py           # RAGAS evaluation script
├── src/
│   ├── apps.py             # LangGraph graph definition
│   ├── nodes.py            # Agent nodes + system prompt
│   ├── tools.py            # campus_db_tool + campus_rag_tool
│   ├── state.py            # Agent state definition
│   └── core/
│       └── config.py       # Environment configuration
├── data/
│   ├── campus.db           # SQLite database
│   ├── iot_sensor_data.csv # Raw IoT data
│   └── campus_rag.index    # FAISS vector index
├── docs/                   # PDF knowledge base + reports
├── tests/
│   ├── test_agent.py       # Agent integration tests
│   ├── test_ci.py          # CI/CD lightweight tests
│   ├── test_ragas_eval.py  # RAGAS evaluation tests
│   └── eval_dataset.json   # RAGAS test dataset
└── .github/
    └── workflows/
        └── ci.yml          # GitHub Actions CI/CD
```

---

##  Switching Between Cloud and On-Premises

### On-Premises (Default)
```
NIM_MODE=onprem
NIM_BASE_URL_ONPREM=http://localhost:8000/v1
NIM_MODEL=/data/shared/nobackup/Qwen2.5-7B-Instruct
```

### Cloud API (NVIDIA NIM)
```
NIM_MODE=cloud
NIM_BASE_URL_CLOUD=https://integrate.api.nvidia.com/v1
NIM_MODEL=meta/llama-3.1-70b-instruct
NIM_API_KEY=your_api_key
```

---

##  Sprint Summary

| Sprint | Focus | Scrum Master | Status |
|---|---|---|---|
| Sprint 1 | Project setup, basic UI | Harshitha | ✅ Done |
| Sprint 2 | NL2SQL pipeline, SQLite | Tarun | ✅ Done |
| Sprint 3 | RAG pipeline, FAISS | Akhila | ✅ Done |
| Sprint 4 | On-premises NIM, vLLM | Ansu | ✅ Done |
| Sprint 5 | User testing, evaluation | Jince | ✅ Done |
| Sprint 6 | Demo prep, final report | Bennet | 🔄 In Progress |

---

## 👥 Team

| Name | Role |
|---|---|
| Akhila Murari | Developer — On-premises NIM, RAG pipeline, UI |
| Tarun | Developer — UI improvements, performance |
| Harshitha Kolipaka | Developer — IoT database, evaluation |
| Bennet | Developer — PDF knowledge base |
| Jince | Developer — LangGraph agent, tool calling |
| Ansu | Developer — Server setup, NIM integration |

---

##  Supervisors
**Dr Di Wu** & **Phu Lai**
Cisco-La Trobe Centre for AI & IoT
La Trobe University 2026

##  Industry Partner
**Scott Mayfield**
Cisco Systems

---

## License
La Trobe University — Academic Project 2026