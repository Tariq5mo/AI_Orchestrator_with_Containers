# AI Orchestrator with Containers 🤖

<div align="center">

![AI Orchestrator Logo](https://img.shields.io/badge/AI-Orchestrator-blue?style=for-the-badge&logo=docker)

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A powerful orchestration system that leverages Large Language Models (LLMs) to interpret natural language requests and orchestrate containerized services.**

</div>

## 🔍 Overview

AI Orchestrator combines the power of LLMs with containerized microservices to create an intelligent workflow automation system. The system interprets high-level natural language requests, determines the appropriate processing pipeline, and executes containerized tasks in the optimal sequence—all without requiring technical syntax knowledge from users.

> "Summarize this article" → Text Summarization Container → Concise Summary

## ✨ Key Features

- **🧠 LLM-Powered Decision Engine:** Utilizes Groq's API to analyze user requests and determine optimal container execution strategy
- **📦 Containerized Microservices:** Modular processing tasks isolated in Docker containers for maximum flexibility and scalability
- **🔀 Smart Orchestration:** Automatically executes containers in the optimal sequence based on request semantics
- **💻 Dual Interfaces:** Access via intuitive web UI or powerful command-line interface
- **⚠️ Resilient Fallback:** Rule-based container selection ensures operation even when LLM API is unavailable
- **⚡ Performance Optimization:** Parallel execution of compatible tasks for improved throughput
- **🔧 Extensible Architecture:** Easily add new containers to extend system capabilities

## 🏗️ Project Structure

```
├── containers/                  # Containerized processing services
│   ├── data_cleaning/           # Text normalization service
│   ├── sentiment_analysis/      # Sentiment analysis service
│   └── text_summarization/      # Text summarization service
├── orchestrator/                # Core orchestration logic
│   ├── app.py                   # Flask web application
│   ├── llm_integration.py       # LLM decision engine
│   ├── orchestrator.py          # Container orchestration logic
│   └── templates/               # Web interface templates
├── tests/                       # Comprehensive test suite
│   ├── run_tests.py             # Test runner
│   └── test_*.py                # Component-specific tests
├── .env                         # Environment variables (API keys)
├── requirements.txt             # Python dependencies
├── debug_orchestrator.py        # Debugging utility
└── run.sh                       # Startup script
```

## 🧰 Containerized Services

### 📝 Data Cleaning (`data-cleaning`)

Prepares text for further processing by normalizing format and structure.

- **Functions:**
  - Removes special characters and punctuation
  - Normalizes whitespace and line breaks
  - Converts text to lowercase for consistency
- **Input:** Raw text (string)
- **Output:** Cleaned, normalized text (string)
- **Use case:** Pre-processing step for other containers

### 😊 Sentiment Analysis (`sentiment-analysis`)

Evaluates the emotional tone and polarity of text content.

- **Algorithm:** Word frequency analysis with sentiment lexicon
- **Features:**
  - Identifies positive and negative expressions
  - Accounts for intensifiers and negations
  - Calculates normalized sentiment score
- **Input:** Text (raw or cleaned)
- **Output:** JSON with sentiment score (-1 to 1) and classification
- **Use case:** Customer feedback analysis, social media monitoring

### 📄 Text Summarization (`text-summarization`)

Creates concise summaries while preserving key information.

- **Algorithm:** Extractive summarization based on sentence importance scoring
- **Features:**
  - Identifies and extracts the most informative sentences
  - Uses term frequency for content importance evaluation
  - Configurable summary length (specify number of sentences)
- **Input:** Text (raw or cleaned)
- **Output:** Summarized text
- **Use case:** Document distillation, article summarization

## 🚀 Getting Started

### Prerequisites

- **Docker:** Engine version 19.03 or higher
- **Python:** 3.9 or higher with pip
- **Groq API Key:** For LLM-based decision making ([Get a key here](https://console.groq.com/))

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/ai-orchestrator.git
   cd ai-orchestrator
   ```

2. **Set up virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key:**

   ```bash
   cp .env.example .env
   # Edit .env and add: LLM_API_KEY=your_groq_api_key_here
   ```

5. **Build and start the system:**

   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   **Or build containers individually:**

   ```bash
   docker build -t ai-orchestrator/data-cleaning containers/data_cleaning/
   docker build -t ai-orchestrator/sentiment-analysis containers/sentiment_analysis/
   docker build -t ai-orchestrator/text-summarization containers/text_summarization/
   ```

## 📊 Usage Examples

### 🌐 Web Interface

Experience the most user-friendly way to interact with the AI Orchestrator.

1. **Start the web server:**

   ```bash
   cd orchestrator
   python app.py
   ```

2. **Open your browser:** Navigate to `http://localhost:5000`

3. **Interact naturally:** Enter your request and provide input text

   ![Web Interface Example](https://img.shields.io/badge/Web-Interface-blue?style=for-the-badge)

### 💻 Command Line Interface

Powerful options for automation and integration with other tools.

#### Basic Text Processing

```bash
python orchestrator/orchestrator.py \
  --request "Clean this text and analyze sentiment" \
  --input-text "This is AMAZING! I love this product so much!!!"
```

#### Processing Files

```bash
python orchestrator/orchestrator.py \
  --request "Summarize this text" \
  --input-file some_article.txt \
  --output-file summary.txt
```

#### Advanced Parameters

```bash
# Specify summary length
python orchestrator/orchestrator.py \
  --request "Summarize this text to 2 sentences" \
  --input-file long_article.txt \
  --output-file summary.txt

# Enable parallel processing
python orchestrator/orchestrator.py \
  --request "Clean this text" \
  --input-text "Multiple samples to clean" \
  --parallel
```

### 🗣️ Example Natural Language Requests

The system understands a wide range of natural language instructions:

| Request Type | Example Phrases |
|-------------|----------------|
| **Text Cleaning** | "Clean this text" <br> "Remove special characters from this text" <br> "Normalize this content" |
| **Sentiment Analysis** | "Analyze sentiment of this review" <br> "Is this feedback positive or negative?" <br> "Determine the emotional tone of this text" |
| **Text Summarization** | "Summarize this article" <br> "Create a brief summary of this text" <br> "Condense this content" |
| **Multi-step Processing** | "Clean this text and then analyze its sentiment" <br> "Summarize this text after cleaning it" |
| **Parameterized Requests** | "Summarize this text to 3 sentences" <br> "Give me a 2-sentence summary" |

## 🧪 Testing

The project includes a comprehensive test suite to ensure reliable operation.

```bash
# Run the full test suite
python tests/run_tests.py

# Run specific component tests
python -m unittest tests/test_containers.py
python -m unittest tests/test_llm_integration.py
python -m unittest tests/test_orchestrator.py
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Container Build Failures** | Ensure Docker is running and you have sufficient permissions |
| **LLM API Errors** | Verify your Groq API key is valid and properly set in the `.env` file |
| **Missing Dependencies** | Run `pip install -r requirements.txt` to install required packages |
| **File Mounting Issues** | Check Docker installation and permissions for volumes |
| **Groq Client Errors** | If you see "proxies" errors, update with `pip install groq==0.4.1` |

### Debug Mode

For more detailed insights during development:

```bash
export LOG_LEVEL=DEBUG
python orchestrator/orchestrator.py --request "Your request" --input-text "Your text"
```

### Advanced Debugging

For introspecting the orchestration flow:

```bash
python debug_orchestrator.py --request "Your request" --input-file your_file.txt
```

## 🛠️ Extending the System

### Adding New Container Services

1. **Create a container directory:**

   ```bash
   mkdir -p containers/new_service
   ```

2. **Implement the processing script:**

   ```python
   #!/usr/bin/env python3
   import sys

   def your_processing_function(data):
       # Your custom processing logic here
       return processed_data

   if __name__ == "__main__":
       # Standard input handling
       if len(sys.argv) > 1:
           with open(sys.argv[1], 'r') as f:
               data = f.read()
       else:
           data = sys.stdin.read()

       # Process data
       result = your_processing_function(data)

       # Standard output handling
       if len(sys.argv) > 2:
           with open(sys.argv[2], 'w') as f:
               f.write(result)
       else:
           print(result)
   ```

3. **Create a Dockerfile:**

   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY your_script.py /app/
   RUN chmod +x /app/your_script.py
   ENTRYPOINT ["python", "your_script.py"]
   CMD []
   ```

4. **Build the container:**

   ```bash
   docker build -t ai-orchestrator/new-service containers/new_service/
   ```

5. **Register the container:**
   Update the `available_containers` dictionary in `orchestrator/llm_integration.py`:

   ```python
   self.available_containers = {
       # Existing containers...
       "new-service": "Description of what your new service does",
   }
   ```

## 📈 Performance Considerations

- **Parallel Execution:** Use the `--parallel` flag for increased throughput when processing multiple independent tasks
- **Container Optimization:** Minimize image size by using slim base images and multi-stage builds
- **Resource Allocation:** Set Docker resource limits for containers in production environments
- **Caching:** Consider implementing a cache for frequent LLM API calls to reduce latency and costs

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
