# AI Orchestrator with Containers

A flexible system that uses Large Language Models to interpret high-level user requests and execute appropriate containerized tasks.

## Features

- **LLM Integration:** Uses Groq's API to analyze user requests and determine which containers to run
- **Containerized Services:** Modular processing tasks isolated in Docker containers
- **Flexible Orchestration:** Executes containers in the optimal sequence based on the request
- **Multiple Interfaces:** Access via web UI or command-line

## Containerized Services

- **Data Cleaning:** Removes special characters, normalizes spaces, and converts text to lowercase
- **Sentiment Analysis:** Evaluates text sentiment using word frequency analysis
- **Text Summarization:** Extracts the most important sentences from a text to create a concise summary

## Setup Instructions

### Prerequisites

- Docker installed
- Python 3.9+ with pip
- A Groq API key (get one from [Groq's website](https://console.groq.com/))

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/ai-orchestrator.git
   cd ai-orchestrator
   ```

2. Install Python dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Add your Groq API key to the `.env` file:

   ```
   LLM_API_KEY=your_groq_api_key_here
   ```

4. Build the Docker containers:

   ```
   docker build -t ai-orchestrator/data-cleaning containers/data_cleaning/
   docker build -t ai-orchestrator/sentiment-analysis containers/sentiment_analysis/
   docker build -t ai-orchestrator/text-summarization containers/text_summarization/
   ```

## Usage

### Web Interface

Start the web server:

```
cd orchestrator
python app.py
```

Then open a browser and navigate to `http://localhost:5000`

### Command Line Interface

Basic usage:

```
python orchestrator/orchestrator.py --request "Clean this text and analyze sentiment" --input-text "This is AMAZING! I love this product so much!!!"
```

Using input/output files:

```
python orchestrator/orchestrator.py --request "Summarize this text" --input-file article.txt --output-file summary.txt
```

### Example Requests

- "Clean this text and analyze its sentiment"
- "Summarize this article"
- "Clean and summarize this text"
- "Analyze the sentiment of this review"

## Architecture

1. User submits a request with text input
2. LLM analyzes the request to determine which containers to run
3. Orchestrator executes containers in sequence
4. Each container's output becomes the input for the next container
5. Final results are collected and returned to the user

## Development

### Adding New Containers

To add a new container:

1. Create a new directory in the `containers` folder
2. Implement your processing script with stdin/stdout or file I/O
3. Create a Dockerfile
4. Build the container
5. Update the `available_containers` dictionary in `llm_integration.py`

## License

MIT
