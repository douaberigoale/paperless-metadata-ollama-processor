import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from models.document import Document
from models.postprocessed_document import PostProcessedDocument
from services.paperless.document_service import DocumentService


class TestDocumentService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.doc_service = DocumentService(self.mock_logger, 'http://api_url', 'test_token')

    @patch('services.paperless.document_service.requests.get')
    def test_get_document_success(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.text = '{"id": 1, "title": "Test Document", "created_date": "2023-09-18", "content": "This is the document content", "correspondent": 2, "document_type": 3, "tags": [1, 2, 3]}'
        mock_response.json.return_value = {
            'id': 1,
            'title': 'Test Document',
            'created_date': '2023-09-18',
            'content': 'This is the document content',
            'correspondent': 2,
            'document_type': 3,
            'tags': [1, 2, 3]
        }
        mock_get.return_value = mock_response

        # when
        document = self.doc_service.get_document(1)

        # then
        self.assertIsInstance(document, Document)
        self.assertEqual(document.id, 1)
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.created_date, '2023-09-18')
        self.assertEqual(document.text, 'This is the document content')
        self.assertEqual(document.correspondent_id, 2)
        self.assertEqual(document.document_type_id, 3)
        self.assertEqual(document.tag_ids, [1, 2, 3])
        self.mock_logger.log_error.assert_not_called()

    @patch('services.paperless.document_service.requests.get')
    def test_get_document_empty_response(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ''  # Empty response
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_get.return_value = mock_response

        # when / then
        with self.assertRaises(ValueError) as context:
            self.doc_service.get_document(1)

        # assert
        self.assertEqual(str(context.exception), "Empty response for document ID 1")

        # assert
        self.mock_logger.log_error.assert_called_once_with("Value error: Empty response for document ID 1", unittest.mock.ANY)

    @patch('services.paperless.document_service.requests.get')
    def test_get_document_non_json_response(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<!DOCTYPE html>'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response

        # when / then
        with self.assertRaises(ValueError) as context:
            self.doc_service.get_document(1)

        # assert
        self.assertEqual(str(context.exception), "Non-JSON response for document ID 1: <!DOCTYPE html>")

        # assert
        self.mock_logger.log_error.assert_called_once_with(
            "Value error: Non-JSON response for document ID 1: <!DOCTYPE html>", unittest.mock.ANY
        )

    @patch('services.paperless.document_service.requests.get')
    def test_get_document_json_decode_error(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "invalid json"
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_get.return_value = mock_response
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "invalid json", 0)

        # when / then
        with self.assertRaises(requests.exceptions.JSONDecodeError):
            self.doc_service.get_document(1)

        # assert
        self.mock_logger.log_error.assert_called_once_with(
            "JSON decode error: Expecting value: line 1 column 1 (char 0), Response: invalid json", unittest.mock.ANY
        )

    @patch('services.paperless.document_service.requests.get')
    def test_get_document_http_error(self, mock_get):
        # given
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        # when / then
        with self.assertRaises(requests.exceptions.HTTPError):
            self.doc_service.get_document(999)

        # assert
        self.mock_logger.log_error.assert_called_once_with(
            "Request exception: 404 Not Found, Response: No response", unittest.mock.ANY
        )

    @patch('services.paperless.document_service.requests.patch')
    def test_update_document_success(self, mock_patch):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        post_processed_doc = PostProcessedDocument(
            title='Updated Title',
            created='2024-09-19',
            correspondent=2,
            document_type=3,
            tags=[1, 2, 3]
        )

        # when
        status_code = self.doc_service.update_document(1, post_processed_doc)

        # then
        self.assertEqual(status_code, 200)
        mock_patch.assert_called_once_with(
            'http://api_url/documents/1/',
            json={'title': 'Updated Title', 'created': '2024-09-19', 'correspondent': 2, 'document_type': 3,
                  'tags': [1, 2, 3]},
            headers={'Authorization': 'Token test_token'}
        )
        self.mock_logger.log.assert_called_once_with(
            "Updating Paperless document with metadata: {'title': 'Updated Title', 'created': '2024-09-19', 'correspondent': 2, 'document_type': 3, 'tags': [1, 2, 3]}")

    @patch('services.paperless.document_service.requests.patch')
    def test_update_document_failure(self, mock_patch):
        # given
        mock_patch.side_effect = Exception("Internal Server Error")

        post_processed_doc = PostProcessedDocument(
            title='Failed Update',
            created=None,
            correspondent=None,
            document_type=None,
            tags=[]
        )

        # when / then
        with self.assertRaises(Exception) as context:
            self.doc_service.update_document(1, post_processed_doc)

        # assert
        self.assertEqual(str(context.exception), "Internal Server Error")

        # assert
        self.mock_logger.log_error.assert_called_once_with(
            "Unexpected error updating document ID 1: Internal Server Error"
        )


if __name__ == '__main__':
    unittest.main()
