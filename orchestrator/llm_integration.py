#!/usr/bin/env python3
import os
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('llm_integration')

# Load environment variables
load_dotenv()

class LLMDecisionEngine:
    def __init__(self):
        """Initialize the LLM decision engine with error handling"""
        # Initialize with mock LLM functionality as default
        self.api_key = os.getenv("LLM_API_KEY")
        self.client = None
        self.use_mock = True

        if self.api_key:
            try:
                logger.info("Attempting to initialize Groq LLM client")
                import groq
                self.client = groq.Client(api_key=self.api_key)
                self.use_mock = False
                logger.info("Successfully initialized Groq LLM client")
            except ImportError as e:
                logger.warning(f"Groq library not installed: {e}")
                logger.info("Falling back to mock LLM implementation")
            except TypeError as e:
                logger.warning(f"Error initializing Groq client: {e}")
                logger.info("Trying alternate initialization method")
                try:
                    # Attempt alternate initialization without problematic parameters
                    import groq
                    # Create a custom client without the proxies parameter
                    self.client = groq.Client(api_key=self.api_key)
                    self.use_mock = False
                    logger.info("Successfully initialized Groq LLM client using alternate method")
                except Exception as inner_e:
                    logger.error(f"Failed with alternate initialization method: {inner_e}")
                    logger.info("Falling back to mock LLM implementation")
            except Exception as e:
                logger.error(f"Unexpected error initializing LLM client: {e}")
                logger.info("Falling back to mock LLM implementation")
        else:
            logger.warning("No LLM_API_KEY found in environment variables")
            logger.info("Using mock LLM responses")

        self.model = "mixtral-8x7b-32768"  # Choose an appropriate model

        # Define available containers and their descriptions
        self.available_containers = {
            "data-cleaning": "Cleans text by removing special characters, normalizing spaces, and converting to lowercase",
            "sentiment-analysis": "Analyzes the sentiment of text, providing a score from -1 (negative) to 1 (positive)",
            "text-summarization": "Creates a concise summary of longer text by extracting key sentences"
        }

        # Log the operational mode
        if self.use_mock:
            logger.info("LLM Decision Engine initialized in MOCK mode")
        else:
            logger.info(f"LLM Decision Engine initialized with model: {self.model}")

    def determine_containers(self, user_request, sample_text=None):
        """Ask the LLM which containers to run based on the user request with robust error handling"""
        logger.info(f"Processing request: '{user_request[:50]}...' (truncated)")

        # If using mock responses, determine containers based on keywords
        if self.use_mock:
            containers = self._mock_determine_containers(user_request)
            logger.info(f"Mock mode determined containers: {containers}")
            return containers

        # Build sample text snippet
        text_sample = ""
        if sample_text:
            text_sample = f"Sample of the input text: '{sample_text[:100]}...'"
            logger.debug(f"Including sample text snippet: {text_sample}")

        # Build the system prompt
        system_prompt = f"""You are an AI orchestrator that decides which containers to run based on user requests.

Available containers:
{self._format_container_descriptions()}

Your task is to determine which containers should be executed and in what order based on the user's request.
Return ONLY a valid JSON array of container names in execution order. Include only containers from the available list.

Examples:
User: "Clean this text and analyze its sentiment"
Output: ["data-cleaning", "sentiment-analysis"]

User: "Summarize this article"
Output: ["text-summarization"]

User: "Clean and summarize this text"
Output: ["data-cleaning", "text-summarization"]
"""

        try:
            logger.debug("Calling LLM API")
            # Call the LLM with timeout
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User request: {user_request}\n{text_sample}"}
                ],
                max_tokens=200,
                response_format={"type": "json_object"},
                timeout=10  # Add timeout to prevent hanging
            )

            # Extract and parse the response
            content = response.choices[0].message.content
            logger.debug(f"Received LLM response: {content[:100]}...")

            try:
                # Handle both array and object responses
                result = json.loads(content)
                if isinstance(result, dict) and "containers" in result:
                    containers = result["containers"]
                elif isinstance(result, list):
                    containers = result
                else:
                    logger.warning(f"Unexpected LLM response format: {content[:100]}...")
                    containers = []

                # Validate containers
                valid_containers = []
                for container in containers:
                    if container in self.available_containers:
                        valid_containers.append(container)
                    else:
                        logger.warning(f"LLM suggested invalid container: '{container}'")

                if not valid_containers and containers:
                    logger.warning("None of the suggested containers are valid. Falling back to mock implementation.")
                    return self._mock_determine_containers(user_request)

                logger.info(f"Valid containers determined: {valid_containers}")
                return valid_containers

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Raw response: {content[:200]}...")
                logger.info("Falling back to mock implementation")
                return self._mock_determine_containers(user_request)

        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            logger.info("Falling back to mock implementation")
            return self._mock_determine_containers(user_request)

    def _mock_determine_containers(self, user_request):
        """Provide mock container selection based on keywords in the request"""
        logger.debug("Using mock container determination")
        request_lower = user_request.lower()
        containers = []

        # Simple keyword matching
        if "clean" in request_lower or "remove" in request_lower:
            containers.append("data-cleaning")
            logger.debug("Mock: Adding data-cleaning container")

        if any(word in request_lower for word in ["sentiment", "analyze", "feeling", "emotion", "positive", "negative"]):
            containers.append("sentiment-analysis")
            logger.debug("Mock: Adding sentiment-analysis container")

        if any(word in request_lower for word in ["summarize", "summary", "shorten", "brief", "concise"]):
            containers.append("text-summarization")
            logger.debug("Mock: Adding text-summarization container")

        # If no containers matched or the request is ambiguous, use a default
        if not containers:
            logger.info("No specific containers matched. Using default container.")
            containers = ["data-cleaning"]

        logger.info(f"Mock determination selected containers: {containers}")
        return containers

    def _format_container_descriptions(self):
        """Format container descriptions for the prompt"""
        return "\n".join([f"- {name}: {desc}" for name, desc in self.available_containers.items()])

# Test the LLM integration
if __name__ == "__main__":
    engine = LLMDecisionEngine()
    test_request = "Clean my text and analyze sentiment"
    containers = engine.determine_containers(test_request)
    print(f"Request: {test_request}")
    print(f"Containers to run: {containers}")