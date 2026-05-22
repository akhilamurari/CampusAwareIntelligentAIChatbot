# 🤖 CampusAware AI

CampusAware AI is an intelligent campus assistant chatbot built for La Trobe University in collaboration with the Cisco AI & IoT Centre, Bundoora. Students and staff can ask questions in plain English and get answers about campus room conditions, parking, WiFi, safety, library hours, and courses — all powered by AI running entirely on the university's own servers. No data leaves the building.

> Built as part of CSE5IDP Industry Development Project — Semester 1, 2026

> 🔗 Live System: https://glorify-overcome-provoke.ngrok-free.dev

> 📁 Server: La Trobe aiotcentre-03 — Cisco AI & IoT Centre, Bundoora

> 🏆 SUS Score: 87/100 (Grade B — Excellent) | RAGAS Score: 0.91/1.0

## 🏁 First Time Setup

Only do this once when setting up on a new server from scratch.

### 1. Clone & Install

```bash
git clone https://github.com/akhilamurari/CampusAwareIntelligentAIChatbot.git
cd CampusAwareIntelligentAIChatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install langgraph-checkpoint-sqlite
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your paths:

```
NIM_MODE=onprem
NIM_BASE_URL_ONPREM=http://localhost:8000/v1
NIM_MODEL=/data/shared/nobackup/Qwen2.5-7B-Instruct
NVIDIA_API_KEY=not-required
SQLITE_DB_PATH=/path/to/data/campus.db
CHECKPOINT_DB_PATH=/path/to/data/checkpoints.db
FAISS_L2_THRESHOLD=1.5
```

The `.env` file is listed in `.gitignore` — it will never be pushed to GitHub. Never put real credentials in `.env.example`.

### 3. Generate IoT Data & Build Knowledge Base

```bash
mkdir -p data
python3 generate_iot_data.py    # Creates 48,960 sensor records across 17 rooms
python3 ingest.py               # Processes 10 campus PDFs into FAISS index
```

This only needs to be done once. After this your `data/campus.db` and `faiss_index/` are ready.

### 4. Start the vLLM Model Server

```bash
tmux new-session -d -s vllm
tmux send-keys -t vllm "source ~/miniconda3/bin/activate && \
CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server \
--model /data/shared/nobackup/Qwen2.5-7B-Instruct \
--port 8000 --dtype bfloat16 --gpu-memory-utilization 0.65 \
--max-model-len 4096 --enable-auto-tool-choice \
--tool-call-parser hermes" Enter
```

Wait 2–3 minutes for the model to load, then verify it is ready:

```bash
curl http://localhost:8000/v1/models
```

### 5. Start the App

```bash
tmux new-session -d -s app
tmux send-keys -t app "cd ~/CampusAwareIntelligentAIChatbot && \
source venv/bin/activate && \
streamlit run app.py --server.port 8502 --server.address 0.0.0.0" Enter
```

### 6. Start ngrok Tunnel

```bash
tmux new-session -d -s ngrok
tmux send-keys -t ngrok "cd ~/CampusAwareIntelligentAIChatbot && ./ngrok http 8502" Enter
```

Check your public URL at `http://localhost:4040` and share it with your team.

### 7. Verify Everything is Running

```bash
tmux ls
# Must show: app, ngrok, vllm

curl http://localhost:8000/v1/models   # vLLM running ✅
curl http://localhost:8502             # Streamlit running ✅
curl http://localhost:4040/api/tunnels # ngrok URL ✅
```

### 8. Register First Student Account

```bash
source venv/bin/activate
python3 create_student.py
```

Or students can self-register directly on the Sign Up tab in the browser.

## 🔄 Daily Startup (Returning Users)

Already set up? Each day just do these 4 steps — the full setup above is not needed again.

**Step 1 — SSH into the server**
```bash
ssh -p 6022 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au
source ~/miniconda3/bin/activate
```

**Step 2 — Check all 3 sessions are running**
```bash
tmux ls
```
You must see `app`, `ngrok`, `vllm`. If all 3 are there, go to Step 3.

**Step 3 — Generate fresh IoT data**
```bash
cd ~/CampusAwareIntelligentAIChatbot
source venv/bin/activate
python3 generate_iot_data.py
```

**Step 4 — Open the browser**

https://glorify-overcome-provoke.ngrok-free.dev


### 🔴 If tmux ls Shows Nothing (All Sessions Gone)

This happens if the server was restarted. Start everything from scratch in this order:

**Step 1 — Start vLLM first**
```bash
tmux new-session -d -s vllm
tmux send-keys -t vllm "source ~/miniconda3/bin/activate && CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server --model /data/shared/nobackup/Qwen2.5-7B-Instruct --port 8000 --dtype bfloat16 --gpu-memory-utilization 0.65 --max-model-len 4096 --enable-auto-tool-choice --tool-call-parser hermes" Enter
```
⏳ Wait 2 minutes before moving to Step 2 — the model needs time to load.

**Step 2 — Start Streamlit**
```bash
tmux new-session -d -s app
tmux send-keys -t app "cd ~/CampusAwareIntelligentAIChatbot && source venv/bin/activate && streamlit run app.py --server.port 8502 --server.address 0.0.0.0" Enter
```

**Step 3 — Start ngrok**
```bash
tmux new-session -d -s ngrok
tmux send-keys -t ngrok "cd ~/CampusAwareIntelligentAIChatbot && ./ngrok http 8502" Enter
```

**Step 4 — Verify all 3 are running**
```bash
tmux ls
# Should show: app, ngrok, vllm
```

**Step 5 — Generate IoT data**
```bash
python3 generate_iot_data.py
```

Then open the URL in your browser and you should see the login page. 🔐

## ⚡ Quick Code Update

Pushed a change to GitHub and need it live on the server straight away?

```bash
git pull origin main
tmux attach -t app
# Press Ctrl+C to stop the running app
streamlit run app.py --server.port 8502 --server.address 0.0.0.0
# Press Ctrl+B then D to detach and leave it running
```

## 🧠 How It Works

The chatbot has two AI pipelines running together behind the scenes.

### 🗄️ NL2SQL — Live Room Data

Converts your plain English question into a SQL query and searches a live IoT sensor database with 48,960 records across 17 campus rooms, covering 7 sensor types — temperature, humidity, CO2, noise, light, occupancy, and air quality.

- Ask: *"Find me a quiet room to study"*
- The agent writes SQL, queries the database, and returns a ranked list

All SQL is validated before execution. DROP, DELETE, INSERT, UPDATE, and injection attempts are blocked automatically before they reach the database.

### 📄 RAG — Campus Documents

Searches across 10 official La Trobe campus PDFs using semantic vector search. Covers parking fees, WiFi setup, safety services, library hours, student accommodation rules, and course information.

- Ask: *"What are the white bay parking fees?"*
- The agent finds the most relevant document chunks and answers directly from them

### 🔐 Student Login & Sessions

Students register with their 8-digit student ID and a password. Passwords are hashed with SHA-256 and a salt before storage — never stored in plain text. Sessions use 32-byte cryptographic random tokens with a 5-minute expiry, stored server-side in SQLite. Nothing sensitive is kept in the browser.

## 🧱 Project Structure
CampusAwareIntelligentAIChatbot/
│
├── app.py                          # Streamlit UI — login, chat, sidebar IoT stats
├── agent.py                        # LangGraph agent entry point
├── auth.py                         # Student registration, login, session tokens
├── generate_iot_data.py            # Generates synthetic IoT sensor data
├── ingest_pdfs.py                  # Loads campus PDFs and builds FAISS index
├── load_to_sqlite.py               # Loads IoT CSV data into SQLite database
├── create_student.py               # Admin script to create student accounts
├── start_app.sh                    # Shell script to start the Streamlit app
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile                      # Docker image definition
├── OPERATIONS_GUIDE.md             # Day-to-day server operations guide
├── requirements.txt                # All Python dependencies with versions
│
├── src/
│   ├── apps.py                     # LangGraph StateGraph and ToolNode setup
│   ├── nodes.py                    # System prompt and assistant node
│   ├── tools.py                    # campus_db_tool (NL2SQL) & campus_rag_tool (RAG)
│   ├── state.py                    # AgentState TypedDict definition
│   ├── nl2sql.py                   # NL2SQL pipeline logic
│   ├── nim_client.py               # NVIDIA NIM API client
│   ├── main.py                     # Entry point for src module
│   └── core/
│       └── config.py               # Centralised configuration
│
├── docs/
│   ├── Admissions_Policy.pdf
│   ├── Campus_WiFi_Guide.txt
│   ├── Code_of_Conduct.pdf
│   ├── Fees and Permits ... Car Parking.pdf
│   ├── Library opening hours.pdf
│   ├── Master of ICT - Melbourne (Bundoora).pdf
│   ├── Melbourne-Campus-Map.pdf
│   ├── Rules-of-Residence-2026.pdf
│   ├── Student_Charter.pdf
│   ├── Student_Support_Policy.pdf
│   ├── la-trobe-student-guide-to-safety.pdf
│   ├── Sprint5_Usability_Report.md  # Sprint 5 usability testing report
│   ├── user_testing_plan.md         # User testing plan
│   ├── user_testing_results.md      # User testing results
│   └── user_testing_responses.csv   # Raw SUS survey responses
│
├── tests/
│   ├── test_agent.py               # Agent integration tests
│   ├── test_ci.py                  # CI/CD pipeline tests
│   ├── test_basic.py               # Basic unit tests
│   ├── test_ragas_eval.py          # RAGAS automated evaluation
│   ├── eval_dataset.json           # RAGAS evaluation dataset
│   └── conftest.py                 # pytest configuration
│
├── faiss/
│   └── faiss_testing.py            # FAISS index testing scripts
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions — linting and tests on every push
│
├── .env.example                    # Environment variable template (no real credentials)
├── .gitignore                      # Excludes .env, venv, data/, faiss_index/
└── README.md
```

## 🧪 What It Can Answer

| Question Type | Example | Answer |
|---|---|---|
| Quiet room | Find me a quiet room to study | Lab-101 at 19.7 dB |
| CO2 levels | Which room has highest CO2? | Lecture-Hall-A at 543 ppm |
| Occupancy | Is Study-Room-1 occupied? | Current occupancy count |
| Parking | White bay parking fees? | $8.45 daily maximum |
| Visitor parking | Visitor car park daily fee? | $17.05 per day |
| WiFi | How to connect to eduroam? | 5-step guide |
| IT support | IT helpdesk number? | 03 9479 2222 |
| Safety | After hours helpline? | 1800 758 360 |
| Security | Security escort number? | 9479 2012 |
| Library | Library face-to-face hours? | 10am–4pm |
| Courses | ICT Masters duration? | 2 years full-time |
| Combined | Quiet room AND parking fees? | Both answered in one response |
| Out of scope | What is the capital of France? | Politely refused — campus only |

## 🛠 Built With

- **LangGraph** — StateGraph agent with conditional routing between tools
- **LangChain** — LLM framework, document loaders, text splitters
- **vLLM** — High-throughput local LLM server with OpenAI-compatible API
- **Qwen2.5-7B-Instruct** — Open source language model (Apache 2.0 licence)
- **FAISS** — Fast vector similarity search for RAG retrieval
- **sentence-transformers/all-MiniLM-L6-v2** — Local embedding model, no API cost
- **Streamlit** — Python-native web UI
- **SQLite** — Zero-config database for IoT data and session management
- **ngrok** — Secure HTTPS tunnel for public access to on-premises server
- **GitHub Actions** — CI/CD with flake8 linting and pytest on every push

## 🖥 Infrastructure

- **Server** — La Trobe Cisco aiotcentre-03, Ubuntu 24 LTS
- **GPU** — 4x NVIDIA L40S (46GB VRAM each) — using CUDA device 1
- **LLM** — Qwen2.5-7B-Instruct served via vLLM on port 8000
- **App** — Streamlit on port 8502, exposed via ngrok HTTPS tunnel
- **Sessions** — Three persistent tmux sessions: vllm, app, ngrok

## 🔴 Troubleshooting

**Check what's running first:**
```bash
tmux ls
```

**If vllm is missing:**
```bash
tmux new-session -d -s vllm
tmux send-keys -t vllm "source ~/miniconda3/bin/activate && CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server --model /data/shared/nobackup/Qwen2.5-7B-Instruct --port 8000 --dtype bfloat16 --gpu-memory-utilization 0.65 --max-model-len 4096 --enable-auto-tool-choice --tool-call-parser hermes" Enter
```
Wait 2 minutes before starting Streamlit.

**If app is missing:**
```bash
tmux new-session -d -s app
tmux send-keys -t app "cd ~/CampusAwareIntelligentAIChatbot && source venv/bin/activate && streamlit run app.py --server.port 8502 --server.address 0.0.0.0" Enter
```

**If ngrok is missing:**
```bash
tmux new-session -d -s ngrok
tmux send-keys -t ngrok "cd ~/CampusAwareIntelligentAIChatbot && ./ngrok http 8502" Enter
```

**If sidebar shows "No Sensor Data":**
```bash
cd ~/CampusAwareIntelligentAIChatbot
source venv/bin/activate
python3 generate_iot_data.py
```
Then refresh the browser.

**If ngrok URL has changed:**
```bash
tmux attach -t ngrok
```
Note the new URL on screen, then press Ctrl+B then D. Share the new URL with your team.

## 🤝 Contributing

1. Fork this repo
2. Create a new branch (`git checkout -b feature/xyz`)
3. Make your changes and reference the ticket (`git commit -am 'CF1CT-XX: description'`)
4. Push to your branch (`git push origin feature/xyz`)
5. Open a pull request against main


## 👥 Team

| Name | Contribution |
|---|---|
| Akhila Murari | Lead — NL2SQL, RAG pipeline, auth system, bug fixes, documentation |
| Bennet | Architecture diagrams, deployment guide |
| Jince | LangGraph agent, final report |
| Ansu | vLLM deployment, Docker, server setup |
| Tarun | Streamlit UI, NL2SQL pipeline |
| Harshitha | Project foundation, IoT database |

**Supervisors:** Dr Di Wu & Phu Lai — La Trobe University
**Industry Mentor:** Scott Mayfield — Cisco Systems

## 📄 Licence

Apache 2.0 — CampusAware AI Team, La Trobe University, 2026