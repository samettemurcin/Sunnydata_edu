#!/bin/bash

# Quick start script for ML Model Customization Web App

echo "🚀 Starting ML Model Customization Web App..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p models

# Start Flask server
echo ""
echo "✅ Starting Flask server on http://localhost:5000"
echo "📚 API Documentation: See API_DOCUMENTATION.md"
echo "🎨 Frontend Guide: See FRONTEND_GUIDE.md"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

