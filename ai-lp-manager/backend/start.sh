#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting AI LP Manager backend on port 8000..."
python server.py
