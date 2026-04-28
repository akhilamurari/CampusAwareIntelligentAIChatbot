#!/bin/bash
echo "Starting CampusAware AI..."

echo "Step 1 — Pulling latest changes..."

echo "Step 2 — Activating venv..."
source venv/bin/activate

echo "Step 3 — Starting Streamlit..."
streamlit run app.py &

echo "Waiting for Streamlit to start..."
sleep 10

echo "Step 4 — Starting Ngrok..."
pkill ngrok 2>/dev/null
ngrok http 8512 &

echo "Waiting for Ngrok..."
sleep 5

echo "Step 5 — Opening browser..."
/usr/bin/open "https://glorify-overcome-provoke.ngrok-free.dev"

echo "Done! Share this URL with students:"
echo "https://glorify-overcome-provoke.ngrok-free.dev"