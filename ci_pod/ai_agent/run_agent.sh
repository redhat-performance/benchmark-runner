# prequesite

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

# Kill anything on 8501 first
kill -9 $(lsof -ti tcp:8501) 2>/dev/null || true

# Run Streamlit in the background
nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &

echo "Streamlit running on port 8501: http://localhost:8501"
echo "Logs: streamlit.log"
echo "Press Ctrl+C to stop"
