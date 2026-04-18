#!/bin/bash
echo "Budget Tracker - Quick Start"
echo "============================"
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
python -m pip install -r requirements.txt > /dev/null 2>&1

echo "Initializing database..."
python -c "import database; database.init_database()"

echo ""
echo "Launching application..."
python main.py
