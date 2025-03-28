#!/usr/bin/env python3
import sys
import os
import unittest
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator.app import app

class TestFlaskApp(unittest.TestCase):
    """Test suite for the Flask web application"""

    def setUp(self):
        """Set up test environment"""
        self.app = app.test_client()
        self.app.testing = True
        self.sample_text = "This is a sample text for testing the Flask app."

    def test_index_route(self):
        """Test that the home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # Check that the response contains expected HTML elements
        self.assertIn(b'AI Orchestrator with Containers', response.data)
        self.assertIn(b'<form id="requestForm">', response.data)
        # Fix: The template uses a script tag without the 'type' attribute
        # Update the test to look for the script tag without expecting 'text/javascript'
        self.assertIn(b'<script>', response.data)

    @patch('orchestrator.app.orchestrator')
    def test_process_endpoint_data_cleaning(self, mock_orchestrator):
        """Test the /process endpoint with a data cleaning request"""
        # Mock the orchestrator's response
        mock_result = {
            'request': 'Clean this text',
            'execution_plan': ['data-cleaning'],
            'execution_time': 0.5,
            'results': [
                {
                    'container': 'data-cleaning',
                    'status': 'success',
                    'output_preview': 'this is cleaned text'
                }
            ],
            'output': 'this is cleaned text'
        }
        mock_orchestrator.process_request.return_value = mock_result

        # Make the request to the endpoint
        response = self.app.post('/process',
                                json={
                                    'request': 'Clean this text',
                                    'text': self.sample_text
                                })

        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data['execution_plan'], ['data-cleaning'])
        self.assertEqual(data['output'], 'this is cleaned text')
        self.assertEqual(len(data['results']), 1)

        # Verify orchestrator was called with the right parameters
        mock_orchestrator.process_request.assert_called_once_with(
            'Clean this text', self.sample_text
        )

    @patch('orchestrator.app.orchestrator')
    def test_process_endpoint_sentiment_analysis(self, mock_orchestrator):
        """Test the /process endpoint with a sentiment analysis request"""
        # Mock the orchestrator's response
        mock_result = {
            'request': 'Analyze sentiment',
            'execution_plan': ['sentiment-analysis'],
            'execution_time': 0.4,
            'results': [
                {
                    'container': 'sentiment-analysis',
                    'status': 'success',
                    'output_preview': '{"score": 0.5, "classification": "positive"}'
                }
            ],
            'output': '{"score": 0.5, "positive_words": 2, "negative_words": 0, "classification": "positive"}'
        }
        mock_orchestrator.process_request.return_value = mock_result

        # Make the request to the endpoint
        response = self.app.post('/process',
                                json={
                                    'request': 'Analyze sentiment',
                                    'text': self.sample_text
                                })

        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data['execution_plan'], ['sentiment-analysis'])
        self.assertIn('score', data['output'])
        self.assertIn('classification', data['output'])

    @patch('orchestrator.app.orchestrator')
    def test_process_endpoint_multi_container(self, mock_orchestrator):
        """Test the /process endpoint with a multi-container request"""
        # Mock the orchestrator's response
        mock_result = {
            'request': 'Clean and summarize',
            'execution_plan': ['data-cleaning', 'text-summarization'],
            'execution_time': 1.1,
            'results': [
                {
                    'container': 'data-cleaning',
                    'status': 'success',
                    'output_preview': 'cleaned text'
                },
                {
                    'container': 'text-summarization',
                    'status': 'success',
                    'output_preview': 'summarized text'
                }
            ],
            'output': 'summarized text'
        }
        mock_orchestrator.process_request.return_value = mock_result

        # Make the request to the endpoint
        response = self.app.post('/process',
                                json={
                                    'request': 'Clean and summarize',
                                    'text': self.sample_text
                                })

        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data['execution_plan'], ['data-cleaning', 'text-summarization'])
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['output'], 'summarized text')

    def test_process_endpoint_missing_request(self):
        """Test the /process endpoint with missing request"""
        response = self.app.post('/process',
                                json={
                                    'text': self.sample_text
                                })

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Request and input text are required', data['error'])

    def test_process_endpoint_missing_text(self):
        """Test the /process endpoint with missing text"""
        response = self.app.post('/process',
                                json={
                                    'request': 'Clean this text'
                                })

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('orchestrator.app.orchestrator')
    def test_process_endpoint_orchestrator_error(self, mock_orchestrator):
        """Test the /process endpoint when orchestrator returns an error"""
        mock_result = {
            'error': 'Something went wrong'
        }
        mock_orchestrator.process_request.return_value = mock_result

        response = self.app.post('/process',
                                json={
                                    'request': 'Invalid request',
                                    'text': self.sample_text
                                })

        # Even though there's an error from orchestrator, API returns 200
        # because the request was processed successfully
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('orchestrator.app.orchestrator')
    def test_process_endpoint_exception(self, mock_orchestrator):
        """Test the /process endpoint when an exception is raised"""
        mock_orchestrator.process_request.side_effect = Exception("Test exception")

        response = self.app.post('/process',
                                json={
                                    'request': 'Clean this text',
                                    'text': self.sample_text
                                })

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Test exception')

if __name__ == '__main__':
    unittest.main()