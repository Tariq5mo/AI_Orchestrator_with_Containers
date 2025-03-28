#!/bin/bash

echo "AI Orchestrator with Containers"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Build all containers
echo "Building containers..."
docker build -t ai-orchestrator/data-cleaning containers/data_cleaning/
docker build -t ai-orchestrator/sentiment-analysis containers/sentiment_analysis/
docker build -t ai-orchestrator/text-summarization containers/text_summarization/

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating a template .env file."
    echo "Please edit it to add your Groq API key."
    echo "LLM_API_KEY=your_groq_api_key_here" > .env
fi

# Run the web application
echo "Starting the web server..."
cd orchestrator
python3 app.py