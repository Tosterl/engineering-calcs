#!/bin/bash
# Start the Engineering Calculations Database web application

echo "Starting Engineering Calculations Database..."
python -m src.main --host 0.0.0.0 --port 8080
