#!/usr/bin/env python3
import unittest
import subprocess
import tempfile
import os
import json
import time

class TestContainers(unittest.TestCase):
    """Test suite for the containerized services"""

    def setUp(self):
        """Setup test environment"""
        # Test data
        self.positive_text = "This is excellent and wonderful. I love it very much."
        self.negative_text = "This is terrible and horrible. I hate it."
        self.neutral_text = "This is a simple test sentence with no sentiment."
        self.long_text = """
        AI Orchestration is the practice of managing multiple AI services, models, and tools to work together.
        It can involve deciding which models to use for different tasks, handling data flow between components,
        and ensuring the entire pipeline operates efficiently. Modern orchestration systems often leverage
        containerization for better isolation, scalability, and deployment consistency. When building an AI
        orchestrator, key considerations include how to parse user requests, select appropriate processing steps,
        and combine services in a meaningful sequence to produce valuable results. These systems need to be flexible
        enough to handle various types of AI workloads while maintaining robustness and reliability.
        """

    def test_data_cleaning_container(self):
        """Test that the data cleaning container works as expected"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as input_file:
            input_file.write("This is SOME TEXT!! With punctuation, and CAPITALS.")
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as output_file:
            output_path = output_file.name

        try:
            # Run the container
            subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{input_path}:/app/input",
                "-v", f"{output_path}:/app/output",
                "ai-orchestrator/data-cleaning",
                "/app/input", "/app/output"
            ], check=True)

            # Read the output
            with open(output_path, 'r') as f:
                result = f.read()

            # Verify the result
            self.assertEqual(result.lower(), result)  # Should be lowercase
            self.assertNotIn("!!", result)  # Punctuation should be removed
            self.assertIn("text", result)  # Content should remain
            self.assertNotIn("CAPITALS", result)  # Uppercase should be converted

        finally:
            # Clean up temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

    def test_sentiment_analysis_container_positive(self):
        """Test sentiment analysis with positive text"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as input_file:
            input_file.write(self.positive_text)
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as output_file:
            output_path = output_file.name

        try:
            # Run the container
            subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{input_path}:/app/input",
                "-v", f"{output_path}:/app/output",
                "ai-orchestrator/sentiment-analysis",
                "/app/input", "/app/output"
            ], check=True)

            # Read the output
            with open(output_path, 'r') as f:
                result = json.loads(f.read())

            # Verify the result
            self.assertIn("score", result)
            self.assertIn("classification", result)
            self.assertGreater(result["score"], 0)  # Should be positive
            self.assertEqual(result["classification"], "positive")
            self.assertGreater(result["positive_words"], 0)

        finally:
            # Clean up temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

    def test_sentiment_analysis_container_negative(self):
        """Test sentiment analysis with negative text"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as input_file:
            input_file.write(self.negative_text)
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as output_file:
            output_path = output_file.name

        try:
            # Run the container
            subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{input_path}:/app/input",
                "-v", f"{output_path}:/app/output",
                "ai-orchestrator/sentiment-analysis",
                "/app/input", "/app/output"
            ], check=True)

            # Read the output
            with open(output_path, 'r') as f:
                result = json.loads(f.read())

            # Verify the result
            self.assertIn("score", result)
            self.assertIn("classification", result)
            self.assertLess(result["score"], 0)  # Should be negative
            self.assertEqual(result["classification"], "negative")
            self.assertGreater(result["negative_words"], 0)

        finally:
            # Clean up temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

    def test_text_summarization_container(self):
        """Test that the text summarization container works as expected"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as input_file:
            # Write a longer text
            input_file.write(self.long_text)
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as output_file:
            output_path = output_file.name

        try:
            # Run the container
            subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{input_path}:/app/input",
                "-v", f"{output_path}:/app/output",
                "ai-orchestrator/text-summarization",
                "/app/input", "/app/output", "2"  # Summarize to 2 sentences
            ], check=True)

            # Read the output
            with open(output_path, 'r') as f:
                result = f.read()

            # Verify the result
            self.assertNotEqual(result, "")
            sentences = [s for s in result.split('.') if s.strip()]
            # Should have 2 sentences as specified
            self.assertLessEqual(len(sentences), 2)
            # Should be shorter than the original
            self.assertLess(len(result), len(self.long_text))

        finally:
            # Clean up temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

    def test_container_error_handling(self):
        """Test how containers handle invalid inputs"""
        # Create an empty input file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as input_file:
            input_file.write("")
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as output_file:
            output_path = output_file.name

        try:
            # Test each container with empty input
            containers = ["data-cleaning", "sentiment-analysis", "text-summarization"]

            for container in containers:
                # Run the container
                result = subprocess.run([
                    "docker", "run", "--rm",
                    "-v", f"{input_path}:/app/input",
                    "-v", f"{output_path}:/app/output",
                    f"ai-orchestrator/{container}",
                    "/app/input", "/app/output"
                ], capture_output=True)

                # Verify the containers don't crash with empty input
                self.assertEqual(result.returncode, 0,
                                f"{container} crashed with empty input: {result.stderr.decode('utf-8')}")

                # Check output file exists and has content (even if empty)
                self.assertTrue(os.path.exists(output_path),
                               f"{container} did not create output file")

        finally:
            # Clean up temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass

if __name__ == '__main__':
    unittest.main()