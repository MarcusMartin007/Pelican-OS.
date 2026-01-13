#!/bin/bash

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. Start the server
echo "Starting Pelican Server..."
echo "You should see: 'Uvicorn running on http://127.0.0.1:8000'"
python3 -m uvicorn server:app --reload
