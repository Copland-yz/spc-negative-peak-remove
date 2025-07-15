#!/bin/bash
echo "Starting SPC Negative Peak Removal Tool..."
echo "Installing dependencies if needed..."
pip install -r requirements.txt

echo "Starting Flask server on http://localhost:5001"
python app.py