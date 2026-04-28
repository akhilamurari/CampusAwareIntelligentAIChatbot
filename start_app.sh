#!/bin/bash
echo "🚀 Starting CampusAware AI..."

echo "Step 1 — Pulling latest changes..."
git pull origin main

echo "Step 2 — Starting Streamlit..."
source venv/bin/activate
streamlit run app.py &

echo "Step 3 — Starting Ngrok..."
sleep 3
pkill ngrok
ngrok http 8502

echo "✅ Done! Share the ngrok URL with students!"