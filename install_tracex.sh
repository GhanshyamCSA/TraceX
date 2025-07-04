#!/bin/bash
set -e

# Create and activate virtual environment
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Print run instructions
cat <<EOF

TraceX is installed in the virtual environment.
To start the server, run:

source .venv/bin/activate
python -m extractor.webapp

The app will be available at http://127.0.0.1:55555
EOF 