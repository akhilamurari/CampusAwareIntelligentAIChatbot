# CampusAware AI — Team Operations Guide

> **Project:** CampusAware Intelligent AI Chatbot  
> **Client:** Cisco AI & IoT Centre — La Trobe University  
> **Server:** aiotcentre-03.latrobe.edu.au  

---

## 🔗 Access Details

| Item | Details |
|------|---------|
| **Public URL** | https://glorify-overcome-provoke.ngrok-free.dev |
| **SSH** | `ssh -p 6022 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au` |
| **Streamlit Port** | 8502 |
| **vLLM Port** | 8000 |

---

## ✅ Daily Startup (do this every time)

**Step 1 — SSH into server:**
```bash
ssh -p 6022 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au
source ~/miniconda3/bin/activate
```

**Step 2 — Check all 3 sessions are running:**
```bash
tmux ls
```
You must see: `app`, `ngrok`, `vllm`  
If all 3 are there go to Step 3.  
If any is missing see the section below.

**Step 3 — Generate fresh IoT sensor data:**
```bash
cd ~/CampusAwareIntelligentAIChatbot
source venv/bin/activate
python3 generate_iot_data.py
```

**Step 4 — Open the URL in browser:**
https://glorify-overcome-provoke.ngrok-free.dev

---

## 🔴 If Website is Down

**First check what is running:**
```bash
tmux ls
```

**If `vllm` session is missing:**
```bash
tmux new-session -d -s vllm
tmux send-keys -t vllm "source ~/miniconda3/bin/activate && CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server --model /data/shared/nobackup/Qwen2.5-7B-Instruct --port 8000 --dtype bfloat16 --gpu-memory-utilization 0.65 --max-model-len 4096 --enable-auto-tool-choice --tool-call-parser hermes" Enter
```
Wait 2 minutes for vLLM to fully load before starting Streamlit.

**If `app` session is missing:**
```bash
tmux new-session -d -s app
tmux send-keys -t app "cd ~/CampusAwareIntelligentAIChatbot && source venv/bin/activate && streamlit run app.py --server.port 8502 --server.address 0.0.0.0" Enter
```

**If `ngrok` session is missing:**
```bash
tmux new-session -d -s ngrok
tmux send-keys -t ngrok "cd ~/CampusAwareIntelligentAIChatbot && ./ngrok http 8502" Enter
```

---

## 📡 If Live Stats Show "No Sensor Data"

```bash
cd ~/CampusAwareIntelligentAIChatbot
source venv/bin/activate
python3 generate_iot_data.py
```
Then refresh the browser.

---

## 🔗 If ngrok URL Has Changed

```bash
tmux attach -t ngrok
```
Note the new URL on screen, then press Ctrl+B then D to detach.

Or get URL via curl:
```bash
curl http://localhost:4040/api/tunnels
```

---

## ✅ Verify Everything is Working

```bash
curl http://localhost:8000/v1/models    # vLLM
curl http://localhost:8502              # Streamlit
curl http://localhost:4040/api/tunnels  # ngrok URL
```

---

## 🚀 Deploying Code Changes

**On your local machine:**
```bash
git add .
git commit -m "your message here"
git push origin main
```

**On the server:**
```bash
ssh -p 6022 22104705@students.ltu.edu.au@aiotcentre-03.latrobe.edu.au
cd ~/CampusAwareIntelligentAIChatbot
git pull origin main
```

**Restart Streamlit:**
```bash
tmux attach -t app
```
Press Ctrl+C to stop, then:
```bash
source venv/bin/activate
streamlit run app.py --server.port 8502 --server.address 0.0.0.0
```
Press Ctrl+B then D to detach.

---

## 🗂 Project Structure

```
CampusAwareIntelligentAIChatbot/
├── app.py                  # Streamlit web UI
├── agent.py                # LangGraph AI agent
├── generate_iot_data.py    # Generates live sensor data
├── load_to_sqlite.py       # Loads data into SQLite
├── data/
│   ├── campus.db           # SQLite database
│   └── campus_rag.index    # FAISS index
├── docs/                   # Campus policy documents
├── ngrok                   # ngrok binary
└── venv/                   # Python virtual environment
```

---

## 📞 Team Contacts

| Name | Role |
|------|------|
| Akhila | Sprint 3 Scrum Master — Primary Contact |
| Tarun | Sprint 2 Scrum Master |
| Harshitha | Sprint 1 Scrum Master |
| Bennet | Sprint 6 Scrum Master |
| Jince | Sprint 5 Scrum Master |
| Ansu | Sprint 4 Scrum Master |

**Supervisors:** Dr Di Wu, Phu Lai  
**Industry Mentor:** Scott Mayfield (Cisco)

---

## Important Notes

- Never push `.env` to GitHub — it contains API keys
- vLLM takes 2 minutes to start — be patient after restart
- ngrok URL may change after each restart — update the team if it changes
- IoT data needs to be regenerated manually by running `generate_iot_data.py`
- SSH password — contact Akhila if you need access

---

Last updated: Sprint 7 — May 2026
