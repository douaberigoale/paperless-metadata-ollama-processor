import unittest
from unittest.mock import patch, Mock, MagicMock
from logic.OllamaService import OllamaService
from logic.FileLoader import FileLoader


class OllamaServiceTests(unittest.TestCase):

    def setUp(self):
        # Mock the logger
        self.mock_logger = MagicMock()

        # Mock the FileLoader and its load method
        self.mock_file_loader = MagicMock(spec=FileLoader)
        self.mock_file_loader.load.return_value = """Extract metadata from "{truncated_text}". Tags: {existing_tags}, Types: {existing_types}, Correspondents: {existing_correspondents}"""

        # Initialize OllamaService with mocked logger and file loader
        self.ollama_service = OllamaService(self.mock_logger, "url", "./prompt", "gemma2:2b", 200, self.mock_file_loader, )

    @patch('requests.post')
    def test_call_success(self, mock_post):
        # given
        ocr_text = "This is a sample OCR text that is quite long and needs truncating"
        existing_tags = ['tag1', 'tag2']
        existing_types = ['type1']
        existing_correspondents = ['correspondent1']

        truncated_text = ' '.join(ocr_text.split()[:100])

        mock_response = Mock()
        mock_response.iter_lines.return_value = [b'{"tags": ["tag1"], "types": ["type1"]}']
        mock_post.return_value = mock_response

        # when
        result = self.ollama_service.call(ocr_text, existing_tags, existing_types, existing_correspondents)

        # then
        expected_prompt = f"""Extract metadata from "{truncated_text}". Tags: {', '.join(existing_tags)}, Types: {', '.join(existing_types)}, Correspondents: {', '.join(existing_correspondents)}"""
        expected_data = {
            "model": "gemma2:2b",
            "prompt": expected_prompt
        }
        mock_post.assert_called_once_with('url', json=expected_data, stream=True)
        self.assertEqual(result, {"tags": ["tag1"], "types": ["type1"]})

    @patch('requests.post')
    def test_call_truncates_text(self, mock_post):
        # given
        ocr_text = "word " * 250  # 250 words; should truncate to 200 words
        existing_tags = ['tag1']
        existing_types = ['type1']
        existing_correspondents = ['correspondent1']

        mock_response = Mock()
        mock_response.iter_lines.return_value = [b'{"tags": ["tag1"], "types": ["type1"]}']
        mock_post.return_value = mock_response

        # when
        result = self.ollama_service.call(ocr_text, existing_tags, existing_types, existing_correspondents)

        # then
        truncated_text = ' '.join(ocr_text.split()[:200])
        expected_prompt = f"""Extract metadata from "{truncated_text}". Tags: {', '.join(existing_tags)}, Types: {', '.join(existing_types)}, Correspondents: {', '.join(existing_correspondents)}"""
        expected_data = {
            "model": "gemma2:2b",
            "prompt": expected_prompt
        }
        mock_post.assert_called_once_with('url', json=expected_data, stream=True)
        self.assertEqual(result, {"tags": ["tag1"], "types": ["type1"]})

    @patch('requests.post')
    def test_call_ollama_api_failure(self, mock_post):
        # given
        ocr_text = "Some OCR text"
        existing_tags = ['tag1']
        existing_types = ['type1']
        existing_correspondents = ['correspondent1']

        mock_post.side_effect = Exception("API Error")

        # when / then
        with self.assertRaises(Exception):
            self.ollama_service.call(ocr_text, existing_tags, existing_types, existing_correspondents)

        self.mock_logger.log_error.assert_called_once_with("Error calling Ollama API: API Error")


if __name__ == '__main__':
    unittest.main()
