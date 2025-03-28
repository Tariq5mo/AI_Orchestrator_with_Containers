#!/usr/bin/env python3
import sys
import os
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from io import StringIO

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator.orchestrator import Orchestrator

@contextmanager
def captured_output():
    """Capture stdout and stderr for testing"""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestOrchestrator(unittest.TestCase):
    """Test suite for the orchestrator component"""

    def setUp(self):
        """Set up test environment"""
        self.orchestrator = Orchestrator()
        # Create a sample text file
        self.sample_text = "This is a sample text. It is very positive and wonderful. I love testing!"

    @patch('orchestrator.orchestrator.LLMDecisionEngine')
    @patch('subprocess.run')
    def test_process_request_data_cleaning(self, mock_subprocess, mock_llm_engine):
        """Test processing a data cleaning request"""
        # Mock the LLM decision engine
        mock_llm_instance = MagicMock()
        mock_llm_instance.determine_containers.return_value = ["data-cleaning"]
        mock_llm_engine.return_value = mock_llm_instance

        # Create orchestrator with mocked LLM
        orchestrator = Orchestrator()

        # Mock subprocess.run to simulate successful container execution
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Create a patch for reading the output file
        with patch('builtins.open', unittest.mock.mock_open(read_data="cleaned text")):
            # Process the request
            result = orchestrator.process_request("Clean this text", self.sample_text)

        # Verify results
        self.assertEqual(result["execution_plan"], ["data-cleaning"])
        self.assertEqual(result["results"][0]["status"], "success")
        self.assertEqual(result["output"], "cleaned text")
        self.assertIn("execution_time", result)

        # Verify the LLM was called with the right parameters
        mock_llm_instance.determine_containers.assert_called_once()
        self.assertEqual(
            mock_llm_instance.determine_containers.call_args[0][0],
            "Clean this text"
        )

    @patch('orchestrator.orchestrator.LLMDecisionEngine')
    @patch('subprocess.run')
    def test_process_request_multiple_containers(self, mock_subprocess, mock_llm_engine):
        """Test processing a request with multiple containers"""
        # Mock the LLM decision engine
        mock_llm_instance = MagicMock()
        mock_llm_instance.determine_containers.return_value = [
            "data-cleaning", "sentiment-analysis"
        ]
        mock_llm_engine.return_value = mock_llm_instance

        # Create orchestrator with mocked LLM
        orchestrator = Orchestrator()

        # Mock subprocess.run to simulate successful container execution
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Set up a more robust file mock that can handle all the file operations
        mock_open = MagicMock()
        # For the initial write of the input text
        initial_file_handle = MagicMock()

        # For reading the first output (data cleaning)
        first_read_handle = MagicMock()
        first_read_handle.__enter__.return_value.read.return_value = "cleaned text"

        # For reading the second output (sentiment analysis)
        second_read_handle = MagicMock()
        second_read_handle.__enter__.return_value.read.return_value = '{"score": 0.5, "classification": "positive"}'

        # For reading the final output
        final_read_handle = MagicMock()
        final_read_handle.__enter__.return_value.read.return_value = '{"score": 0.5, "classification": "positive"}'

        # Configure mock to return different handles for different file paths
        def side_effect(filename, *args, **kwargs):
            if 'output_0.txt' in str(filename):
                return first_read_handle
            elif 'output_1.txt' in str(filename):
                return second_read_handle
            else:
                return final_read_handle

        mock_open.side_effect = side_effect

        with patch('builtins.open', mock_open):
            # Process the request
            result = orchestrator.process_request(
                "Clean this text and analyze sentiment", self.sample_text
            )

        # Verify results
        self.assertEqual(result["execution_plan"], ["data-cleaning", "sentiment-analysis"])
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["status"], "success")
        self.assertEqual(result["results"][1]["status"], "success")
        self.assertEqual(result["output"], '{"score": 0.5, "classification": "positive"}')

        # Verify subprocess.run was called twice (once for each container)
        self.assertEqual(mock_subprocess.call_count, 2)

    @patch('orchestrator.orchestrator.LLMDecisionEngine')
    def test_process_request_no_containers(self, mock_llm_engine):
        """Test handling when no containers are determined"""
        # Mock the LLM decision engine to return no containers
        mock_llm_instance = MagicMock()
        mock_llm_instance.determine_containers.return_value = []
        mock_llm_engine.return_value = mock_llm_instance

        # Create orchestrator with mocked LLM
        orchestrator = Orchestrator()

        # Process the request
        result = orchestrator.process_request("Unknown request", self.sample_text)

        # Verify error is returned
        self.assertIn("error", result)
        self.assertEqual(
            result["error"], "Could not determine which containers to run"
        )

    @patch('orchestrator.orchestrator.LLMDecisionEngine')
    def test_process_request_container_error(self, *args):
        """Test handling of container execution errors"""
        import subprocess

        # Create a completely separate orchestrator instance for this test
        test_orchestrator = Orchestrator()

        # Replace the LLM decision engine with a simple mock
        test_orchestrator.llm = MagicMock()
        test_orchestrator.llm.determine_containers.return_value = ["data-cleaning", "sentiment-analysis"]

        # Create a patched version of subprocess.run that will fail for sentiment-analysis
        original_run = subprocess.run

        def mock_run(args, **kwargs):
            if "ai-orchestrator/sentiment-analysis" in args:
                error = subprocess.CalledProcessError(1, args)
                error.stderr = "Container execution error"
                raise error
            return original_run(["echo", "Test successful"], **kwargs)

        # Apply the patch
        subprocess.run = mock_run

        try:
            # Run the test with our patched function
            with patch('builtins.open') as mock_open:
                # Mock file operations
                mock_file = MagicMock()
                mock_file.__enter__.return_value.read.return_value = "Test content"
                mock_file.__enter__.return_value.write = MagicMock()
                mock_open.return_value = mock_file

                # Process the request
                result = test_orchestrator.process_request(
                    "Clean this text and analyze sentiment", self.sample_text
                )

            # Verify results show the error
            self.assertEqual(result["execution_plan"], ["data-cleaning", "sentiment-analysis"])
            self.assertEqual(len(result["results"]), 2)
            self.assertEqual(result["results"][0]["status"], "success")
            self.assertEqual(result["results"][1]["status"], "error")

        finally:
            # Restore the original function
            subprocess.run = original_run

    def test_process_request_input_file(self):
        """Test processing a request with input from a file"""
        # Create a temporary file with sample text
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(self.sample_text)
            temp_file = f.name

        try:
            # Patch the LLM and subprocess to avoid actual execution
            with patch('orchestrator.orchestrator.LLMDecisionEngine') as mock_llm_engine:
                # Mock the LLM
                mock_llm_instance = MagicMock()
                mock_llm_instance.determine_containers.return_value = ["data-cleaning"]
                mock_llm_engine.return_value = mock_llm_instance

                # Mock subprocess
                with patch('subprocess.run') as mock_subprocess:
                    mock_subprocess.return_value = MagicMock(returncode=0)

                    # Mock file reading
                    with patch('builtins.open', unittest.mock.mock_open(read_data="cleaned text")):
                        # Process the request - FIX: Use self.orchestrator instead of orchestrator
                        result = self.orchestrator.process_request(
                            "Clean this text", None, temp_file
                        )

            # Verify results
            self.assertEqual(result["execution_plan"], ["data-cleaning"])
            self.assertEqual(result["results"][0]["status"], "success")

        finally:
            os.unlink(temp_file)

    def test_process_request_invalid_input(self):
        """Test handling of invalid inputs"""
        # Test with no input text and no file
        result = self.orchestrator.process_request("Clean this text", None, None)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No input text provided")

        # Test with non-existent input file
        result = self.orchestrator.process_request(
            "Clean this text", None, "/path/to/nonexistent/file"
        )
        self.assertIn("error", result)
        self.assertIn("Could not read input file", result["error"])

if __name__ == '__main__':
    unittest.main()