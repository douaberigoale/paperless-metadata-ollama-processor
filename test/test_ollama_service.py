import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
import json
from services.ollama_service import OllamaService
from models.extracted_metadata import ExtractedMetadata


class TestOllamaService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_prompt_creator = MagicMock()
        self.mock_response_processor = MagicMock()

        self.ollama_service = OllamaService(
            logger=self.mock_logger,
            api_url="http://api_url",
            model_name="test_model",
            prompt_creator=self.mock_prompt_creator,
            response_processor=self.mock_response_processor
        )

    @patch('services.ollama_service.requests.post')
    def test_extract_metadata_success(self, mock_post):
        # Given: A successful response from the Ollama API
        ocr_text = "Sample OCR text"
        self.mock_prompt_creator.create_prompt.return_value = "Generated Prompt"

        # Mock response processor methods
        self.mock_response_processor.process.return_value = '{"title": "Sample Title", "date": "2023-09-18", "correspondent": "John Doe", "document_type": "Invoice", "tags": ["tag1", "tag2"]}'
        mock_response = Mock()
        mock_post.return_value = mock_response

        # Simulate JSON response to be returned as a dictionary
        self.mock_response_processor.get_json = MagicMock(
            return_value=json.loads(self.mock_response_processor.process.return_value))

        # When: extract_metadata is called
        metadata = self.ollama_service.extract_metadata(ocr_text)

        # Then: The metadata should be correctly extracted and returned
        expected_metadata = ExtractedMetadata(
            title="Sample Title",
            created_date="2023-09-18",
            correspondent="John Doe",
            document_type="Invoice",
            tags=["tag1", "tag2"]
        )

        self.assertEqual(metadata.title, expected_metadata.title)
        self.assertEqual(metadata.created_date, expected_metadata.created_date)
        self.assertEqual(metadata.correspondent, expected_metadata.correspondent)
        self.assertEqual(metadata.document_type, expected_metadata.document_type)
        self.assertEqual(metadata.tags, expected_metadata.tags)

    @patch('services.ollama_service.requests.post')
    def test_extract_metadata_http_error(self, mock_post):
        # Given: A request to the API that results in a RequestException
        ocr_text = "Sample OCR text"
        self.mock_prompt_creator.create_prompt.return_value = "Generated Prompt"
        mock_post.side_effect = requests.exceptions.RequestException("API failure")

        # When / Then: extract_metadata should raise a RequestException and log the error
        with self.assertRaises(requests.exceptions.RequestException):
            self.ollama_service.extract_metadata(ocr_text)

        self.mock_logger.log_error.assert_called_once_with(
            "HTTP error calling Ollama API: API failure"
        )

if __name__ == '__main__':
    unittest.main()
