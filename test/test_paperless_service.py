import unittest
from unittest.mock import patch, Mock, MagicMock
from requests.exceptions import HTTPError

from services.paperless_service import PaperlessService


class PaperlessServiceTests(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.paperless_api = PaperlessService(self.mock_logger, "url", "token")

    @patch('requests.get')
    def test_extract_text_success(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.json.return_value = {'content': 'Some OCR text'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # when
        result = self.paperless_api.get_document_text(1)

        # then
        self.assertEqual(result, 'Some OCR text')
        self.mock_logger.log.assert_called_once_with('Extracting text for document ID: 1')

    @patch('requests.get')
    def test_extract_text_no_content(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # when
        result = self.paperless_api.get_document_text(1)

        # then
        self.assertIsNone(result)
        self.mock_logger.log.assert_called_once_with('Extracting text for document ID: 1')

    @patch('requests.get')
    def test_extract_text_http_error(self, mock_get):
        # given
        mock_get.side_effect = HTTPError("404 Client Error")

        # when / then
        with self.assertRaises(HTTPError):
            self.paperless_api.get_document_text(1)

        self.mock_logger.log_error.assert_called_once_with("HTTP error: 404 Client Error", unittest.mock.ANY)

    @patch('requests.get')
    def test_extract_text_general_exception(self, mock_get):
        # given
        mock_get.side_effect = Exception("Some other error")

        # when / then
        with self.assertRaises(Exception):
            self.paperless_api.get_document_text(1)

        self.mock_logger.log_error.assert_called_once_with("Error extracting OCR text: Some other error",
                                                           unittest.mock.ANY)

    @patch('requests.get')
    def test_get_existing_metadata_success(self, mock_get):
        # given
        mock_tags_response = Mock()
        mock_tags_response.json.return_value = {'results': [{'name': 'tag1'}, {'name': 'tag2'}]}

        mock_types_response = Mock()
        mock_types_response.json.return_value = {'results': [{'name': 'type1'}]}

        mock_correspondents_response = Mock()
        mock_correspondents_response.json.return_value = {'results': [{'name': 'correspondent1'}]}

        mock_get.side_effect = [mock_tags_response, mock_types_response, mock_correspondents_response]

        # when
        tags, types, correspondents = self.paperless_api.get_existing_metadata()

        # then
        self.assertEqual(tags, ['tag1', 'tag2'])
        self.assertEqual(types, ['type1'])
        self.assertEqual(correspondents, ['correspondent1'])

    @patch('requests.get')
    def test_get_existing_metadata_http_error(self, mock_get):
        # given
        mock_get.side_effect = HTTPError("500 Server Error")

        # when / then
        with self.assertRaises(HTTPError):
            self.paperless_api.get_existing_metadata()

        self.mock_logger.log_error.assert_called_once_with("Error retrieving existing data: 500 Server Error")

    @patch('requests.patch')
    def test_update_document_success(self, mock_patch):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        # when
        status_code = self.paperless_api.update_document(1, {'tags': ['tag1'], 'types': ['type1']})

        # then
        self.assertEqual(status_code, 200)
        self.mock_logger.log.assert_called_once_with(
            "Updating Paperless document ID 1 with metadata: {'tags': ['tag1'], 'types': ['type1']}")

    @patch('requests.patch')
    def test_update_document_http_error(self, mock_patch):
        # given
        mock_patch.side_effect = HTTPError("400 Bad Request")

        # when / then
        with self.assertRaises(HTTPError):
            self.paperless_api.update_document(1, {'tags': ['tag1'], 'types': ['type1']})

        self.mock_logger.log_error.assert_called_once_with("Error updating Paperless document ID 1: 400 Bad Request")

    @patch('requests.patch')
    def test_update_document_general_exception(self, mock_patch):
        # given
        mock_patch.side_effect = Exception("Unexpected error")

        # when / then
        with self.assertRaises(Exception):
            self.paperless_api.update_document(1, {'tags': ['tag1'], 'types': ['type1']})

        self.mock_logger.log_error.assert_called_once_with("Error updating Paperless document ID 1: Unexpected error")


if __name__ == '__main__':
    unittest.main()
