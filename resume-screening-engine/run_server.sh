# #!/bin/bash
# cd /Users/chandren/Documents/GitHub/intelligent-resume-screening-engine/resume-screening-engine
# /Users/chandren/Documents/GitHub/intelligent-resume-screening-engine/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000



#!/bin/bash
# Navigate to the directory where the script is located
cd "$(dirname "$0")"
# Run uvicorn using the environment's python
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000