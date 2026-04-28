#!/bin/bash
cd /Users/priyanshnarang/Desktop/stepone-ai/backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
echo "Server starting on <http://localhost:8000>"
sleep 3
curl -s "<http://localhost:8000/health>" || echo "Server is starting..."
