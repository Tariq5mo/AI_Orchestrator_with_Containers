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
- **⚡ Parallel Execution:** Support for running compatible tasks concurrently for improved performance

## 🖥️ Project Structure

```
ai_orchestrator/
├── containers/                # Containerized microservices
│   ├── data_cleaning/         # Text normalization service
│   ├── sentiment_analysis/    # Sentiment analysis service
│   └── text_summarization/    # Text summarization service
├── orchestrator/              # Core orchestration logic
│   ├── app.py                 # Flask web application
│   ├── orchestrator.py        # Container orchestration logic
│   ├── llm_integration.py     # LLM decision engine
│   └── templates/             # Web interface templates
├── tests/                     # Test suite
│   ├── run_tests.py           # Test runner script
│   └── test_*.py              # Component tests
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
└── run.sh                     # Startup script
```

## 🔧 Installation

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Groq API key (for LLM integration)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/AI_Orchestrator_with_Containers.git
   cd AI_Orchestrator_with_Containers
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env file to add your Groq API key
   # LLM_API_KEY=your_groq_api_key_here
   ```

5. **Build the Docker containers**

   ```bash
   # Using the automated script
   ./run.sh

   # Or manually
   docker build -t ai-orchestrator/data-cleaning containers/data_cleaning/
   docker build -t ai-orchestrator/sentiment-analysis containers/sentiment_analysis/
   docker build -t ai-orchestrator/text-summarization containers/text_summarization/
   ```

## 🚀 Usage

### Web Interface

1. **Start the web server**

   ```bash
   python orchestrator/app.py
   ```

2. **Open your browser and navigate to**

   ```
   http://localhost:5000
   ```

3. **Enter your natural language request in the input field and submit**

### Command Line Interface

Process text directly:

```bash
python orchestrator/orchestrator.py --request "Clean this text and analyze sentiment" --input-text "This is AMAZING! I love this product so much!!!"
```

Process from file and save to output file:

```bash
python orchestrator/orchestrator.py --request "Summarize this text" --input-file some_article.txt --output-file summary.txt
```

Advanced usage with parameters:

```bash
# Summarize to a specific number of sentences
python orchestrator/orchestrator.py --request "Summarize this text to 2 sentences" --input-file long_article.txt

# Enable parallel execution
python orchestrator/orchestrator.py --request "Clean this text" --input-text "Text to clean" --parallel
```

## 📊 Supported Services

The AI Orchestrator currently supports the following containerized services:

| Service | Description | Example Command |
|---------|-------------|----------------|
| **Text Summarization** | Extracts key sentences to create concise summaries | "Summarize this article" |
| **Data Cleaning** | Normalizes text by removing special characters and standardizing format | "Clean this dataset" |
| **Sentiment Analysis** | Analyzes emotional tone with positive/negative scoring | "What's the sentiment of this review?" |

## 🧪 Examples

### Data Cleaning

```bash
python orchestrator/orchestrator.py --request "Clean this text" --input-file messy_text.txt --output-file cleaned_text.txt
```

Input:

```
THIS is a SAMPLE text with LOTS of CAPITALS!!!
  It also has   extra   spaces,  and @#$%&* special characters.
```

Output:

```
this is a sample text with lots of capitals it also has extra spaces and special characters
```

### Sentiment Analysis

```bash
python orchestrator/orchestrator.py --request "Is this review positive?" --input-text "This product is amazing! I love it."
```

Output:

```json
{
  "score": 0.845,
  "positive_words": 2,
  "negative_words": 0,
  "classification": "positive"
}
```

### Text Summarization with Parameters

```bash
python orchestrator/orchestrator.py --request "Summarize this article to 3 sentences" --input-file long_article.txt
```

## 🏗️ Architecture

The system consists of three main components:

1. **Orchestrator Engine**: Core logic that processes requests, makes decisions, and manages container lifecycle
2. **LLM Integration**: Connects to Groq's API for natural language understanding and decision making
3. **Container Services**: Independent microservices that perform specific data processing tasks

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Request   │────▶│   Orchestrator  │────▶│  LLM Decision   │
└─────────────────┘     │     Engine      │◀────│     Engine      │
                        └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Container      │
                        │  Execution      │
                        └────────┬────────┘
                                 │
                        ┌────────┴────────┐
                        ▼                 ▼
            ┌─────────────────┐  ┌─────────────────┐
            │ Data Processing │  │ Result          │
            │ Containers      │  │ Formatting      │
            └─────────────────┘  └─────────────────┘
```

## 🧪 Testing

Run the comprehensive test suite to verify all system components:

```bash
python tests/run_tests.py
```

Individual component tests can be run as follows:

```bash
python -m unittest tests/test_orchestrator.py
python -m unittest tests/test_containers.py
python -m unittest tests/test_llm_integration.py
```

## ⚠️ Troubleshooting

### Common Issues

- **Container Build Failures**: Ensure Docker is running and you have sufficient permissions
- **LLM API Errors**: Verify your Groq API key is valid and properly set in the `.env` file
- **Missing Dependencies**: Run `pip install -r requirements.txt` to install required packages
- **File Mounting Issues**: For Docker-related errors, check your Docker installation and permissions
- **Groq Client Errors**: If you see "proxies" errors, update the groq package with `pip install groq==0.4.1`

### Debug Mode

For more detailed logging:

```bash
export LOG_LEVEL=DEBUG
python orchestrator/orchestrator.py --request "Your request" --input-text "Your text"
```

## 🛠️ Extending the System

### Adding New Containers

To create a new container:

1. **Create a directory** in `containers/` (e.g., `containers/new_service/`)
2. **Implement your processing script** with standard input/output handling:

   ```python
   if __name__ == "__main__":
       # Read from stdin or file
       if len(sys.argv) > 1:
           with open(sys.argv[1], 'r') as f:
               data = f.read()
       else:
           data = sys.stdin.read()

       # Process data
       result = your_processing_function(data)

       # Output to file or stdout
       if len(sys.argv) > 2:
           with open(sys.argv[2], 'w') as f:
               f.write(result)
       else:
           print(result)
   ```

3. **Create a Dockerfile**
4. **Build the container**: `docker build -t ai-orchestrator/new-service containers/new_service/`
5. **Register the container** in `orchestrator/llm_integration.py`

## 🤝 Contributing

Contributions are welcome! Here's how you can help improve the AI Orchestrator:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact & Support

For questions or issues, please open an issue on GitHub or contact the project maintainers.

---

<div align="center">

**Made with ❤️ by Tariq Omer**

</div>
