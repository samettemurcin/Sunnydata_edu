#!/bin/bash

# Start script for frontend (simple HTTP server)

echo "🌐 Starting Frontend Server..."
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✅ Starting Python HTTP server on http://localhost:8000"
    echo "📂 Serving files from: frontend/"
    echo ""
    echo "Open your browser and go to: http://localhost:8000"
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    cd frontend
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "✅ Starting Python HTTP server on http://localhost:8000"
    echo "📂 Serving files from: frontend/"
    echo ""
    echo "Open your browser and go to: http://localhost:8000"
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    cd frontend
    python -m http.server 8000
else
    echo "❌ Python not found. Please install Python 3."
    exit 1
fi

