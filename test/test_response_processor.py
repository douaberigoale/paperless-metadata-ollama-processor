import unittest
from unittest.mock import MagicMock
import json
from services.response_processor import ResponseProcessor


class TestResponseProcessor(unittest.TestCase):

    def setUp(self):
        # Given: A ResponseProcessor instance with a mocked logger
        self.mock_logger = MagicMock()
        self.response_processor = ResponseProcessor(logger=self.mock_logger)

    def test_get_json_valid(self):
        # Given: A valid JSON response
        response = '{"title": "Sample Title"}'

        # When: get_json is called
        result = self.response_processor.get_json(response)

        # Then: No exception should be raised and it should return valid JSON
        self.assertEqual({'title': 'Sample Title'}, result)

    def test_get_json_valid_with_markdown(self):
        # Given: A valid JSON response, but with markdown
        response = '```json{"title": "Sample Title"}```'

        # When: get_json is called
        result = self.response_processor.get_json(response)

        # Then: No exception should be raised and it should return valid JSON
        self.assertEqual({'title': 'Sample Title'}, result)

    def test_get_json_invalid(self):
        # Given: An invalid JSON response
        response = "Invalid JSON content"

        # When / Then: get_json should raise a ValueError and log the error
        with self.assertRaises(ValueError):
            self.response_processor.get_json(response)

        self.mock_logger.log_error.assert_called_once_with(f"Could not find valid JSON structure in the response: {response}")

    def test_process_success(self):
        # Given: A response with valid JSON lines
        responses = MagicMock()
        responses.iter_lines.return_value = [
            '{"response": "Part1"}',
            '{"response": "Part2"}'
        ]

        # When: process is called
        result = self.response_processor.process(responses)

        # Then: The full response should be concatenated correctly
        self.assertEqual(result, "Part1Part2")

    def test_process_with_invalid_json(self):
        # Given: A response with an invalid JSON line
        responses = MagicMock()
        responses.iter_lines.return_value = [
            '{"response": "Part1"}',
            'Invalid JSON Line'
        ]

        # When / Then: process should raise JSONDecodeError and log the error
        with self.assertRaises(json.JSONDecodeError):
            self.response_processor.process(responses)

        self.mock_logger.log_error.assert_called_once_with("Error parsing response from Ollama API: Expecting value: line 1 column 1 (char 0). Chunk: Invalid JSON Line")

    def test_get_response_part_valid(self):
        # Given: A valid JSON response part
        line = '{"response": "Part of the response"}'

        # When: get_response_part is called
        result = self.response_processor.get_response_part(line)

        # Then: The response part should be extracted correctly
        self.assertEqual(result, "Part of the response")

    def test_get_response_part_invalid(self):
        # Given: An invalid JSON line
        line = "Invalid JSON Line"

        # When / Then: get_response_part should raise JSONDecodeError and log the error
        with self.assertRaises(json.JSONDecodeError):
            self.response_processor.get_response_part(line)

        self.mock_logger.log_error.assert_called_once_with(
            "Error parsing response from Ollama API: Expecting value: line 1 column 1 (char 0). Chunk: Invalid JSON Line"
        )

    def test_extract_json_valid(self):
        # Given: A valid response string with JSON content
        response_text = "Some text ```json{\"title\":\"Sample Title\"}``` more text"

        # When: _extract_json is called
        result = self.response_processor._extract_json(response_text)

        # Then: The JSON content should be extracted correctly
        self.assertEqual(result, '{"title":"Sample Title"}')

    def test_extract_json_invalid(self):
        # Given: A response string without valid JSON content
        response_text = "Some text without valid JSON"

        # When / Then: _extract_json should raise ValueError and log the error
        with self.assertRaises(ValueError):
            self.response_processor._extract_json(response_text)

        self.mock_logger.log_error.assert_called_once_with(f"Could not find valid JSON structure in the response: {response_text}")

    def test_extract_json_malformed_json(self):
        # Given: A response string with malformed JSON content
        response_text = "Some text ```json{\"title\":\"Sample Title\"``` more text"  # Missing closing brace

        # When / Then: _extract_json should raise ValueError and log the error
        with self.assertRaises(ValueError):
            self.response_processor._extract_json(response_text)

        self.mock_logger.log_error.assert_called_once_with(f"Could not find valid JSON structure in the response: {response_text}")


if __name__ == '__main__':
    unittest.main()
