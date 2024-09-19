import unittest
from unittest.mock import patch, Mock, MagicMock
from requests.exceptions import HTTPError

from services.paperless_service import PaperlessService


class PaperlessServiceTests(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.paperless_api = PaperlessService(self.mock_logger, "http://localhost", "token")

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

    @patch('requests.get')
    @patch('requests.patch')
    def test_update_document_success_with_append_tags(self, mock_patch, mock_get):
        # given
        mock_document_response = Mock()
        mock_document_response.json.return_value = {
            'title': 'Old Title',
            'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
            'correspondent': None,
            'type': None
        }
        mock_get.return_value = mock_document_response

        mock_patch_response = Mock()
        mock_patch_response.status_code = 200
        mock_patch.return_value = mock_patch_response

        new_metadata = {
            'title': 'New Title',
            'tags': ['tag2', 'tag3'],  # tag2 is a duplicate, should not be added again
            'correspondent': 'New Correspondent',
            'type': 'New Type'
        }

        # when
        status_code = self.paperless_api.update_document(1, new_metadata)

        # then
        self.assertEqual(status_code, 200)

        # Expected metadata (unordered tag comparison)
        expected_metadata = {
            'title': 'New Title',
            'tags': {'tag1', 'tag2', 'tag3'},  # tag3 is added, no duplicates
            'correspondent': 'New Correspondent',
            'type': 'New Type'
        }
        # Compare tags as sets to avoid order sensitivity
        actual_tags = {tag for tag in mock_patch.call_args[1]['json']['tags']}
        self.assertEqual(actual_tags, expected_metadata['tags'])

        self.mock_logger.log.assert_called_with(
            f"Updating Paperless document ID 1 with new metadata: {mock_patch.call_args[1]['json']}"
        )

    @patch('requests.patch')
    @patch('requests.get')
    def test_update_document_does_not_overwrite_non_empty_correspondent_or_type(self, mock_get, mock_patch):
        # given
        mock_document_response = Mock()
        mock_document_response.json.return_value = {
            'title': 'Old Title',
            'tags': [{'name': 'tag1'}],
            'correspondent': 'Existing Correspondent',
            'type': 'Existing Type'
        }
        mock_get.return_value = mock_document_response

        mock_patch_response = Mock()
        mock_patch_response.status_code = 200
        mock_patch.return_value = mock_patch_response

        new_metadata = {
            'title': 'New Title',
            'tags': ['tag2'],
            'correspondent': 'New Correspondent',
            'type': 'New Type'
        }

        # when
        status_code = self.paperless_api.update_document(1, new_metadata)

        # then
        self.assertEqual(status_code, 200)

        expected_metadata = {
            'title': 'New Title',
            'tags': ['tag1', 'tag2'],  # Order does not matter here
            'correspondent': 'Existing Correspondent',
            'type': 'Existing Type'
        }

        actual_metadata = mock_patch.call_args[1]['json']
        self.assertEqual(set(actual_metadata['tags']), set(expected_metadata['tags']))
        self.assertEqual(actual_metadata['title'], expected_metadata['title'])
        self.assertEqual(actual_metadata['correspondent'], expected_metadata['correspondent'])
        self.assertEqual(actual_metadata['type'], expected_metadata['type'])

    @patch('requests.patch')
    @patch('requests.get')
    def test_update_document_http_error(self, mock_get, mock_patch):
        # given
        mock_get_response = Mock()
        mock_get_response.json.return_value = {
            'title': 'Old Title',
            'tags': [{'name': 'tag1'}],
            'correspondent': 'Existing Correspondent',
            'type': 'Existing Type'
        }
        mock_get.return_value = mock_get_response

        mock_patch.side_effect = HTTPError("400 Bad Request")

        # when & then
        with self.assertRaises(HTTPError):
            self.paperless_api.update_document(1, {'tags': ['tag1'], 'types': ['type1']})

    @patch('requests.patch')
    @patch('requests.get')
    def test_update_document_general_exception(self, mock_get, mock_patch):
        # given
        mock_get.return_value = Mock()
        mock_patch.side_effect = Exception("Unexpected error")

        # when
        with self.assertRaises(Exception):
            self.paperless_api.update_document(1, {'tags': ['tag1'], 'types': ['type1']})

        # then
        self.mock_logger.log_error.assert_called_once_with(unittest.mock.ANY)
        actual_call_args = self.mock_logger.log_error.call_args[0][0]
        self.assertIn("Error updating Paperless document ID 1", actual_call_args)


if __name__ == '__main__':
    unittest.main()
